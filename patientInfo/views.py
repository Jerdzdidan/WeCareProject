from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from django.utils import timezone
import re
from patientInfo.models import (
    Patient,
    VitalSigns,
    Vaccination,
    PastMedicalHistory,
    MedicalRecord,
    PresentIllness,
    MedicineTracking,
    VitalSignsRecord
)
from medicineMonitoring.models import Medicine, MedicineStock
from medicineMonitoring.views import update_medicine_date_last_stocked, update_medicine_totals
from residentInfo.models import Resident
from scheduledcheckup.models import ScheduledCheckup
from users.decorators import role_required
from logs.models import Logs
from django.db.models import Sum

# === PATIENT RECORD FUNCTIONALITY ===
@login_required
@role_required(['ADMIN', 'BRGY-STAFF', 'BHW', 'DOCTOR'], 'Patient Information')
def patient_list(request):
    category = request.GET.get('category', '')
    gender = request.GET.get('gender', '')
    street = request.GET.get('street', '') 

    patients = Patient.objects.select_related('resident').all()

    if category:
        patients = patients.filter(resident__category=category)
    if gender:
        patients = patients.filter(resident__gender=gender)
    if street:
        patients = patients.filter(resident__present_address__icontains=street)

    patients = patients.order_by('patientID')

    return render(request, 'patientInfo/patient_list.html', {'patients': patients})

@login_required
@role_required(['BHW'], 'Select patient on the Patient Information')
def patient_select(request):
    available_residents = Resident.objects.filter(patient__isnull=True).order_by('id')
    return render(request, 'patientInfo/patient_select.html', {'available_residents': available_residents})

@login_required
@role_required(['BHW'], 'Create patient on the Patient Information')
def patient_create_details(request, resident_id):
    if not resident_id:
        messages.error(request, "Please select a resident first.")
        return redirect('patient-select')
    
    resident = get_object_or_404(Resident, id=resident_id)
    if hasattr(resident, 'patient'):
        messages.error(request, "This resident is already registered as a patient.")
        return redirect('patient-list')
    
    if request.method == "POST":
        patient = Patient.objects.create(resident=resident)
        
        bp = request.POST.get("bp", "").strip()
        pr = request.POST.get("pr", "").strip()
        temp = request.POST.get("temp", "").strip()
        height = request.POST.get("height", "").strip()
        weight = request.POST.get("weight", "").strip()
        
        try:
            pr_int = int(pr) if pr else None
        except ValueError:
            pr_int = None
        try:
            temp_float = float(temp) if temp else None
        except ValueError:
            temp_float = None
        try:
            height_float = float(height) if height else None
        except ValueError:
            height_float = None
        try:
            weight_float = float(weight) if weight else None
        except ValueError:
            weight_float = None
        
        VitalSigns.objects.create(
            patient=patient,
            blood_pressure=bp or None,
            pulse_rate=pr_int,
            temperature=temp_float,
            height=height_float,
            weight=weight_float,
        )
        
        VitalSignsRecord.objects.create(
            patient=patient,
            blood_pressure=bp or None,
            pulse_rate=pr_int,
            temperature=temp_float,
            height=height_float,
            weight=weight_float,
        )
        
        index = 0
        while True:
            illness_key = f"present_illness[{index}][illness_name]"
            if illness_key in request.POST:
                illness_name = request.POST.get(illness_key, "").strip()
                start_date_str = request.POST.get(f"present_illness[{index}][start_date]", "").strip()
                treatment = request.POST.get(f"present_illness[{index}][treatment]", "").strip()
                
                if not (illness_name or start_date_str or treatment):
                    index += 1
                    continue

                try:
                    start_date = datetime.strptime(start_date_str, "%b %d, %Y").date() if start_date_str else None
                except ValueError:
                    start_date = None
            
                if illness_name and start_date:
                    patient.present_illnesses.create(
                        illness_name=illness_name,
                        start_date=start_date,
                        treatment=treatment
                    )
                index += 1
            else:
                break
        
        hepatitis_a = request.POST.get("vaccinations[hepatitis_a]") == "on"
        hepatitis_b = request.POST.get("vaccinations[vaccinations[hepatitis_b]]") == "on"
        hpv_vaccine = request.POST.get("vaccinations[hpv_vaccine]") == "on"
        pre_announced_vaccine = request.POST.get("vaccinations[pre_announced_vaccine]") == "on"
        typhoid = request.POST.get("vaccinations[typhoid]") == "on"
        mmr = request.POST.get("vaccinations[mmr]") == "on"
        dpt = request.POST.get("vaccinations[dpt]") == "on"
        chicken_pox = request.POST.get("vaccinations[chicken_pox]") == "on"
        tetanus_toxoid = request.POST.get("vaccinations[tetanus_toxoid]") == "on"
        others = request.POST.get("vaccinations[others_text]", "").strip()
        
        Vaccination.objects.create(
            patient=patient,
            hepatitis_a=hepatitis_a,
            hepatitis_b=hepatitis_b,
            hpv_vaccine=hpv_vaccine,
            pre_announced_vaccine=pre_announced_vaccine,
            typhoid=typhoid,
            mmr=mmr,
            dpt=dpt,
            chicken_pox=chicken_pox,
            tetanus_toxoid=tetanus_toxoid,
            others=others
        )
        
        asthma = request.POST.get("past_history[asthma]") == "on"
        anemia = request.POST.get("past_history[anemia]") == "on"
        bad_teeth = request.POST.get("past_history[bad_teeth]") == "on"
        diabetes = request.POST.get("past_history[diabetes]") == "on"
        depression = request.POST.get("past_history[depression]") == "on"
        heart_disease = request.POST.get("past_history[heart_disease]") == "on"
        hearing_problem = request.POST.get("past_history[hearing_problem]") == "on"
        high_blood_pressure = request.POST.get("past_history[high_blood_pressure]") == "on"
        heart_attack = request.POST.get("past_history[heart_attack]") == "on"
        drug_allergy = request.POST.get("past_history[drug_allergy]") == "on"
        allergy_details = request.POST.get("past_history[allergy_details]", "").strip()
        med_history_others = request.POST.get("past_history[others]", "").strip()

        PastMedicalHistory.objects.create(
            patient=patient,
            asthma=asthma,
            anemia=anemia,
            bad_teeth=bad_teeth,
            diabetes=diabetes,
            depression=depression,
            heart_disease=heart_disease,
            hearing_problem=hearing_problem,
            high_blood_pressure=high_blood_pressure,
            heart_attack=heart_attack,
            drug_allergy=drug_allergy,
            allergy_details=allergy_details,
            others=med_history_others
        )
        
        messages.success(request, "Patient record created successfully!")
        return redirect('patient-list')
    
    return render(request, 'patientInfo/patient_create_details.html', {'resident': resident})



@login_required
@role_required(['BHW', 'DOCTOR'], 'Update patient on the Patient Information')
def patient_update(request, pk):
    patient = get_object_or_404(Patient, patientID=pk)
    
    try:
        vital_signs = patient.vital_signs
    except VitalSigns.DoesNotExist:
        vital_signs = None
    vaccination = getattr(patient, 'vaccinations', None)
    past_medical_history = getattr(patient, 'past_medical_history', None)
    
    if request.method == "POST":
        bp = request.POST.get("bp", "").strip()
        pr = request.POST.get("pr", "").strip()
        temp = request.POST.get("temp", "").strip()
        height = request.POST.get("height", "").strip()
        weight = request.POST.get("weight", "").strip()
        
        # Update or create current VitalSigns
        if vital_signs:
            vital_signs.blood_pressure = bp or None
            vital_signs.pulse_rate = pr or None
            vital_signs.temperature = temp or None
            vital_signs.height = height or None
            vital_signs.weight = weight or None
            vital_signs.save()
        else:
            if any([bp, pr, temp, height, weight]):
                vital_signs = VitalSigns.objects.create(
                    patient=patient,
                    blood_pressure=bp or None,
                    pulse_rate=pr or None,
                    temperature=temp or None,
                    height=height or None,
                    weight=weight or None,
                )
        
        # Create a new VitalSignsRecord to log the update
        VitalSignsRecord.objects.create(
            patient=patient,
            blood_pressure=bp or None,
            pulse_rate=pr or None,
            temperature=temp or None,
            height=height or None,
            weight=weight or None,
        )
        
        # Update present illnesses
        patient.present_illnesses.all().delete()
        index = 0
        while True:
            illness_key = f"present_illness[{index}][illness_name]"
            if illness_key in request.POST:
                illness_name = request.POST.get(illness_key, "").strip()
                start_date_str = request.POST.get(f"present_illness[{index}][start_date]", "").strip()
                treatment = request.POST.get(f"present_illness[{index}][treatment]", "").strip()
                
                if not (illness_name or start_date_str or treatment):
                    index += 1
                    continue
                
                try:
                    start_date = datetime.strptime(start_date_str, "%b %d, %Y").date() if start_date_str else None
                except ValueError:
                    start_date = None
               
                if illness_name and start_date:
                    patient.present_illnesses.create(
                        illness_name=illness_name,
                        start_date=start_date,
                        treatment=treatment
                    )
                index += 1
            else:
                break
        
        # Update Vaccination
        hepatitis_a = request.POST.get("vaccinations[hepatitis_a]") == "on"
        hepatitis_b = request.POST.get("vaccinations[hepatitis_b]") == "on"
        hpv_vaccine = request.POST.get("vaccinations[hpv_vaccine]") == "on"
        pre_announced_vaccine = request.POST.get("vaccinations[pre_announced_vaccine]") == "on"
        typhoid = request.POST.get("vaccinations[typhoid]") == "on"
        mmr = request.POST.get("vaccinations[mmr]") == "on"
        dpt = request.POST.get("vaccinations[dpt]") == "on"
        chicken_pox = request.POST.get("vaccinations[chicken_pox]") == "on"
        tetanus_toxoid = request.POST.get("vaccinations[tetanus_toxoid]") == "on"
        others = request.POST.get("vaccinations[others_text]", "").strip()
        
        if vaccination:
            vaccination.hepatitis_a = hepatitis_a
            vaccination.hepatitis_b = hepatitis_b
            vaccination.hpv_vaccine = hpv_vaccine
            vaccination.pre_announced_vaccine = pre_announced_vaccine
            vaccination.typhoid = typhoid
            vaccination.mmr = mmr
            vaccination.dpt = dpt
            vaccination.chicken_pox = chicken_pox
            vaccination.tetanus_toxoid = tetanus_toxoid
            vaccination.others = others
            vaccination.save()
        else:
            if hepatitis_a or hepatitis_b or hpv_vaccine or pre_announced_vaccine or typhoid or mmr or dpt or chicken_pox or tetanus_toxoid or others:
                Vaccination.objects.create(
                    patient=patient,
                    hepatitis_a=hepatitis_a,
                    hepatitis_b=hepatitis_b,
                    hpv_vaccine=hpv_vaccine,
                    pre_announced_vaccine=pre_announced_vaccine,
                    typhoid=typhoid,
                    mmr=mmr,
                    dpt=dpt,
                    chicken_pox=chicken_pox,
                    tetanus_toxoid=tetanus_toxoid,
                    others=others
                )
        
        # Update Past Medical History
        asthma = request.POST.get("past_history[asthma]") == "on"
        anemia = request.POST.get("past_history[anemia]") == "on"
        bad_teeth = request.POST.get("past_history[bad_teeth]") == "on"
        diabetes = request.POST.get("past_history[diabetes]") == "on"
        depression = request.POST.get("past_history[depression]") == "on"
        heart_disease = request.POST.get("past_history[heart_disease]") == "on"
        hearing_problem = request.POST.get("past_history[hearing_problem]") == "on"
        high_blood_pressure = request.POST.get("past_history[high_blood_pressure]") == "on"
        heart_attack = request.POST.get("past_history[heart_attack]") == "on"
        drug_allergy = request.POST.get("past_history[drug_allergy]") == "on"
        allergy_details = request.POST.get("past_history[allergy_details]", "").strip()
        med_history_others = request.POST.get("past_history[others]", "").strip()
        
        if past_medical_history:
            past_medical_history.asthma = asthma
            past_medical_history.anemia = anemia
            past_medical_history.bad_teeth = bad_teeth
            past_medical_history.diabetes = diabetes
            past_medical_history.depression = depression
            past_medical_history.heart_disease = heart_disease
            past_medical_history.hearing_problem = hearing_problem
            past_medical_history.high_blood_pressure = high_blood_pressure
            past_medical_history.heart_attack = heart_attack
            past_medical_history.drug_allergy = drug_allergy
            past_medical_history.allergy_details = allergy_details
            past_medical_history.others = med_history_others
            past_medical_history.save()
        else:
            if (asthma or anemia or bad_teeth or diabetes or depression or heart_disease or
                hearing_problem or high_blood_pressure or heart_attack or drug_allergy or allergy_details):
                PastMedicalHistory.objects.create(
                    patient=patient,
                    asthma=asthma,
                    anemia=anemia,
                    bad_teeth=bad_teeth,
                    diabetes=diabetes,
                    depression=depression,
                    heart_disease=heart_disease,
                    hearing_problem=hearing_problem,
                    high_blood_pressure=high_blood_pressure,
                    heart_attack=heart_attack,
                    drug_allergy=drug_allergy,
                    allergy_details=allergy_details,
                    others=med_history_others
                )
        
        now = datetime.now()
        formatted_date = now.strftime("%b. %d, %Y")
        formatted_time = now.strftime("%I:%M%p")

        Logs.objects.create(
            datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
            timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
            module="Patient Information",
            action="Update Patient",
            performed_to=f"Patient ID - {patient.patientID}: {patient.resident.first_name} {patient.resident.last_name}",
            performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
        )

        messages.success(request, "Patient record updated successfully!")
        return redirect('patient-list')
    
    return render(request, "patientInfo/patient_update.html", {
        "patient": patient,
        "vital_signs": vital_signs,
        "present_illnesses": patient.present_illnesses.all(),
        "vaccination": vaccination,
        "past_medical_history": past_medical_history,
    })


@login_required
@role_required(['BHW'], 'Delete patient on the Patient Information')
def patient_delete_confirm(request, pk):
    try:
        patient = Patient.objects.get(patientID=pk)
    except Patient.DoesNotExist:
        messages.warning(request, "No patient records found!")
        return redirect('patient-list')
    
    now = datetime.now()
    formatted_date = now.strftime("%b. %d, %Y")
    formatted_time = now.strftime("%I:%M%p")

    Logs.objects.create(
        datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
        timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
        module="Patient Information",
        action="Delete Patient",
        performed_to=f"Patient ID - {patient.patientID}: {patient.resident.last_name}, {patient.resident.first_name}",
        performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
    )

    patient.delete()
    messages.success(
        request,
        f"Patient record deleted for {patient.patientID}: {patient.resident.last_name}, {patient.resident.first_name} successfully!"
    )
    return redirect('patient-list')



@login_required
@role_required(['ADMIN', 'BRGY-STAFF', 'BHW', 'DOCTOR'], 'Patient Details')
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, patientID=pk)
    records = patient.medical_records.all().order_by('-last_visited')
    
    # Filter Medical Records by date (using GET keys: start_date and end_date)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%b %d, %Y").date()
            end_date_obj = datetime.strptime(end_date, "%b %d, %Y").date()
            records = records.filter(last_visited__range=[start_date_obj, end_date_obj])
        except ValueError:
            pass
    elif start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%b %d, %Y").date()
            records = records.filter(last_visited__gte=start_date_obj)
        except ValueError:
            pass
    elif end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%b %d, %Y").date()
            records = records.filter(last_visited__lte=end_date_obj)
        except ValueError:
            pass

    medicine_trackings = patient.medicine_trackings.all().order_by('start_date')
    
    # Filter Vital Signs Records by date (using GET keys: vitalsignsfilter_start_date and vitalsignsfilter_end_date)
    vitalsigns_records = patient.vital_signs_records.all().order_by('-recorded_at')
    vs_start = request.GET.get('vitalsignsfilter_start_date')
    vs_end = request.GET.get('vitalsignsfilter_end_date')
    if vs_start and vs_end:
        try:
            vs_start_obj = datetime.strptime(vs_start, "%b %d, %Y").date()
            vs_end_obj = datetime.strptime(vs_end, "%b %d, %Y").date()
            vitalsigns_records = vitalsigns_records.filter(recorded_at__range=[vs_start_obj, vs_end_obj])
        except ValueError:
            pass
    elif vs_start:
        try:
            vs_start_obj = datetime.strptime(vs_start, "%b %d, %Y").date()
            vitalsigns_records = vitalsigns_records.filter(recorded_at__gte=vs_start_obj)
        except ValueError:
            pass
    elif vs_end:
        try:
            vs_end_obj = datetime.strptime(vs_end, "%b %d, %Y").date()
            vitalsigns_records = vitalsigns_records.filter(recorded_at__lte=vs_end_obj)
        except ValueError:
            pass

    return render(request, 'patientInfo/patient_detail.html', {
        'patient': patient,
        'medical_records': records,
        'medicine_trackings': medicine_trackings,
        'vitalsigns_records': vitalsigns_records,
    })



# === MEDICAL RECORD FUNCTIONALITY ===
@login_required
@role_required(['DOCTOR'], 'Create medical record on the Patient Information')
def medical_record_create(request, pk):
    patient = get_object_or_404(Patient, patientID=pk)
    if request.method == "POST":
        concern = request.POST.get('concern', '').strip()
        description = request.POST.get('description', '').strip()
        recommendation = request.POST.get('recommendation', '').strip()
        
        last_visited = datetime.today().date()
        MedicalRecord.objects.create(
            patient=patient,
            concern=concern,
            description=description,
            recommendation=recommendation,
            last_visited=last_visited
        )
        messages.success(request, "Medical record created successfully!")
        return redirect('patient-detail', pk=patient.patientID)
    return render(request, 'patientInfo/medical_record_create.html', {'patient': patient})


@login_required
@role_required(['DOCTOR'], 'Update medical record on the Patient Information')
def medical_record_update(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    if request.method == "POST":
        concern = request.POST.get('concern', '').strip()
        description = request.POST.get('description', '').strip()
        recommendation = request.POST.get('recommendation', '').strip()
        last_visited_str = request.POST.get('last_visited', '').strip()
        try:
            last_visited = datetime.strptime(last_visited_str, "%Y-%m-%d").date()
        except ValueError:
            last_visited = record.last_visited
        record.concern = concern
        record.description = description
        record.recommendation = recommendation
        record.last_visited = last_visited
        record.save()

        now = datetime.now()
        formatted_date = now.strftime("%b. %d, %Y")
        formatted_time = now.strftime("%I:%M%p")

        Logs.objects.create(
            datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
            timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
            module="Patient Information",
            action="Update Medical Record",
            performed_to=f"Medical Record ID - {record.id} for Patient ID - {record.patient.patientID}: {record.patient.resident.last_name}, {record.patient.resident.first_name}",
            performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
        )

        messages.success(request, "Medical record updated successfully!")
        return redirect('patient-detail', pk=record.patient.patientID)
    return render(request, 'patientInfo/medical_record_update.html', {'record': record})

@login_required
@role_required(['DOCTOR'], 'Delete medical record on the Patient Information')
def medical_record_delete(request, patient_pk, record_id):
    try:
        record = MedicalRecord.objects.get(id=record_id)
    except Patient.DoesNotExist:
        messages.warning(request, "No medical records found!")
        return redirect('patient-detail', pk=patient_pk)

    now = datetime.now()
    formatted_date = now.strftime("%b. %d, %Y")
    formatted_time = now.strftime("%I:%M%p")

    Logs.objects.create(
        datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
        timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
        module="Patient Information",
        action="Delete Medical Record",
        performed_to=f"Medical Record ID - {record.id} for Patient ID - {record.patient.patientID}: {record.patient.resident.last_name}, {record.patient.resident.first_name}",
        performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
    )

    record.delete()
    messages.success(request, f"Medical record deleted for {record.patient.patientID}: {record.patient.resident.last_name}, {record.patient.resident.first_name} successfully!")
    return redirect('patient-detail', pk=patient_pk)




# ===== PATIENT_MEDICINE_TRACKING =====
@login_required
@role_required(['DOCTOR'], 'Select medicine on the Patient Information')
def medicine_tracking_select(request, pk):
    patient = get_object_or_404(Patient, patientID=pk)
    available_medicines = Medicine.objects.all().order_by("medicine_name")
    context = {
        "patient": patient,
        "available_medicines": available_medicines,
    }
    return render(request, "patientInfo/medicinetracking_select.html", context)

@login_required
@role_required(['DOCTOR'], 'Select Chief Complaint for Medicine Tracking')
def medicine_tracking_select_chief_complain(request, pk, medicine_id):
    patient = get_object_or_404(Patient, patientID=pk)
    medical_records = patient.medical_records.all().order_by('-last_visited')
    context = {
        "patient": patient,
        "medicine_id": medicine_id,
        "medical_records": medical_records,
    }
    return render(request, "patientInfo/chief_complaint_select.html", context)


@login_required
@role_required(['DOCTOR'], 'Create patient-medicine tracking on the Patient Information')
def medicine_tracking_create_details(request, pk, medicine_id):
    patient = get_object_or_404(Patient, patientID=pk)
    medicine = get_object_or_404(Medicine, id=medicine_id)

    patient_medicine_tracking = MedicineTracking.objects.filter(medicine=medicine)
    releasedQty = patient_medicine_tracking.aggregate(total=Sum('quantity_used'))['total'] or 0

    today = date.today()

    valid_stocks = medicine.stocks.filter(expiration_date__gt=today)

    available_stocks = valid_stocks.filter(quantity__gt=10)
    availableQty = available_stocks.aggregate(total=Sum('quantity'))['total'] or 0

    chief_complain_prefill = request.GET.get("chief_complain", "")

    if request.method == "POST":
        quantity_str = request.POST.get("quantity", "").strip()
        total_dosage = request.POST.get("total_dosage", "").strip()
        frequency = request.POST.get("frequency", "").strip()
        chief_complain = request.POST.get("chief_complain", "").strip()
        date_given_str = request.POST.get("date_given", "").strip()
        follow_up_date_str = request.POST.get("follow_up_date", "").strip()
        start_date_str = request.POST.get("start_date", "").strip()
        end_date_str = request.POST.get("end_date", "").strip()
        notes = request.POST.get("notes", "").strip()

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive.")
        except ValueError:
            messages.error(request, "Please enter a valid quantity.")
            return redirect("medicine-tracking-create-details", pk=patient.patientID, medicine_id=medicine.id)
        

        try:
            date_given = datetime.strptime(date_given_str, "%Y-%m-%d").date() if date_given_str else date.today()
        except ValueError:
            date_given = date.today()

        try:
            follow_up_date = datetime.strptime(follow_up_date_str, "%Y-%m-%d").date() if follow_up_date_str else None
        except ValueError:
            follow_up_date = None

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else date.today()
        except ValueError:
            start_date = date.today()

        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
        except ValueError:
            end_date = None

        available_stock = medicine.stocks.filter(
            expiration_date__gt=date.today(),
            quantity__gte=quantity
        ).order_by("expiration_date").first()

        if not available_stock:
            messages.error(request, "Insufficient stock available for the selected medicine.")
            return redirect("medicine-tracking-create-details", pk=patient.patientID, medicine_id=medicine.id,)

        available_stock.quantity -= quantity
        available_stock.save(update_fields=["quantity"])

        tracking = MedicineTracking.objects.create(
            patient=patient,
            medicine=medicine,
            medicine_stock=available_stock,
            quantity_used=quantity,
            total_dosage=total_dosage,
            frequency=frequency,
            chief_complain=chief_complain,
            date_given=date_given,
            follow_up_date=follow_up_date,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
        )

        if follow_up_date:
            ScheduledCheckup.objects.create(
                patient=patient,
                checkup_date=follow_up_date,
                notes=f"Follow-up checkup for medication: {medicine.medicine_name} ({tracking.date_given.strftime('%Y-%m-%d')})"
            )

        update_medicine_totals(medicine)
        update_medicine_date_last_stocked(medicine)

        messages.success(request, "Medicine tracking record created successfully!")
        return redirect("patient-detail", pk=patient.patientID)
    
    context = {
        "patient": patient,
        "medicine": medicine,
        "releasedQty": releasedQty,
        "availableQty": availableQty,
        "chief_complain_prefill": chief_complain_prefill,
    }
    return render(request, "patientInfo/medicinetracking_create_details.html", context)

@login_required
@role_required(['DOCTOR'], 'Update patient-medicine tracking on the Patient Information')
def medicine_tracking_update(request, tracking_id):
    tracking = get_object_or_404(MedicineTracking, id=tracking_id)
    patient = tracking.patient
    medicine = tracking.medicine
    old_quantity = tracking.quantity_used

    patient_medicine_tracking = MedicineTracking.objects.filter(medicine=medicine)
    releasedQty = patient_medicine_tracking.aggregate(total=Sum('quantity_used'))['total'] or 0

    today = date.today()

    valid_stocks = medicine.stocks.filter(expiration_date__gt=today)

    available_stocks = valid_stocks.filter(quantity__gt=10)
    availableQty = available_stocks.aggregate(total=Sum('quantity'))['total'] or 0

    if request.method == "POST":
        quantity_str = request.POST.get("quantity", "").strip()
        frequency = request.POST.get("frequency", "").strip()
        chief_complain = request.POST.get("chief_complain", "").strip()
        date_given_str = request.POST.get("date_given", "").strip()
        follow_up_date_str = request.POST.get("follow_up_date", "").strip()
        start_date_str = request.POST.get("start_date", "").strip()
        end_date_str = request.POST.get("end_date", "").strip()
        notes = request.POST.get("notes", "").strip()

        try:
            new_quantity = int(quantity_str)
            if new_quantity <= 0:
                raise ValueError("Quantity must be positive.")
        except ValueError:
            messages.error(request, "Please enter a valid quantity.")
            return redirect("medicine-tracking-update", tracking_id=tracking.id)

        try:
            new_date_given = datetime.strptime(date_given_str, "%Y-%m-%d").date() if date_given_str else date.today()
        except ValueError:
            new_date_given = date.today()

        try:
            new_follow_up_date = datetime.strptime(follow_up_date_str, "%Y-%m-%d").date() if follow_up_date_str else None
        except ValueError:
            new_follow_up_date = None

        try:
            new_start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else date.today()
        except ValueError:
            new_start_date = date.today()

        try:
            new_end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
        except ValueError:
            new_end_date = None

        quantity_diff = new_quantity - old_quantity

        if quantity_diff > 0:
            additional_needed = quantity_diff
            if tracking.medicine_stock.quantity >= additional_needed:
                tracking.medicine_stock.quantity -= additional_needed
                tracking.medicine_stock.save(update_fields=["quantity"])
            else:
                messages.error(request, "Insufficient stock available for the additional quantity.")
                return redirect("medicine-tracking-update", tracking_id=tracking.id)
        elif quantity_diff < 0:
            tracking.medicine_stock.quantity += abs(quantity_diff)
            tracking.medicine_stock.save(update_fields=["quantity"])

        new_total_dosage = ""
        if medicine.dosage:
            match = re.match(r"^([\d\.]+)\s*(.*)$", medicine.dosage.strip())
            if match:
                base_value = float(match.group(1))
                unit = match.group(2)
                new_total_dosage = f"{new_quantity * base_value} {unit}".strip()

        tracking.quantity_used = new_quantity
        tracking.frequency = frequency
        tracking.chief_complain = chief_complain
        tracking.date_given = new_date_given
        tracking.follow_up_date = new_follow_up_date
        tracking.start_date = new_start_date
        tracking.end_date = new_end_date
        tracking.notes = notes
        tracking.total_dosage = new_total_dosage
        tracking.save()

        if new_follow_up_date:
            ScheduledCheckup.objects.create(
                patient=patient,
                checkup_date=new_follow_up_date,
                notes=f"Follow-up checkup for medication: {medicine.medicine_name} ({tracking.date_given.strftime('%Y-%m-%d')})"
            )

        update_medicine_totals(medicine)
        update_medicine_date_last_stocked(medicine)

        now = datetime.now()
        formatted_date = now.strftime("%b. %d, %Y")
        formatted_time = now.strftime("%I:%M%p")

        Logs.objects.create(
            datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
            timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
            module="Patient Information",
            action="Update Medicine Tracking",
            performed_to=f"Medicine Tracking ID - {tracking.id} for {patient.patientID}: {patient.resident.last_name}, {patient.resident.first_name} (Medicine: {medicine.medicine_name})",
            performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
        )

        messages.success(request, "Medicine tracking record updated successfully!")
        return redirect("patient-detail", pk=patient.patientID)
    
    context = {
        "tracking": tracking,
        "patient": patient,
        "medicine": medicine,
        "releasedQty": releasedQty,
        "availableQty": availableQty
    }
    return render(request, "patientInfo/medicinetracking_update.html", context)


@login_required
@role_required(['DOCTOR'], 'Delete patient-medicine tracking on the Patient Information')
def medicine_tracking_delete(request, tracking_id):
    tracking = get_object_or_404(MedicineTracking, id=tracking_id)

    now = datetime.now()
    formatted_date = now.strftime("%b. %d, %Y")
    formatted_time = now.strftime("%I:%M%p")

    Logs.objects.create(
        datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
        timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
        module="MedicineTracking",
        action="Delete Medicine Tracking",
        performed_to=f"Medicine Tracking ID - {tracking.id} for {tracking.patient.patientID}: {tracking.patient.resident.last_name}, {tracking.patient.resident.first_name} (Medicine: {tracking.medicine.medicine_name})",
        performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
    )

    tracking.delete()
    messages.success(request, "Medicine tracking record deleted successfully!")
    return redirect(request.META.get('HTTP_REFERER', '/'))


# === VITAL SIGNS FUNCTIONALITY ===
@login_required
@role_required(['BHW', 'DOCTOR'], 'Create vital signs on the Patient Information')
def vital_signs_create(request, pk):
    patient = get_object_or_404(Patient, patientID=pk)
    
    if request.method == 'POST':
        blood_pressure = request.POST.get('blood_pressure')
        pulse_rate = request.POST.get('pulse_rate')
        temperature = request.POST.get('temperature')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        
        try:
            pulse_rate = int(pulse_rate) if pulse_rate else None
        except ValueError:
            pulse_rate = None
        try:
            temperature = float(temperature) if temperature else None
        except ValueError:
            temperature = None
        try:
            height = float(height) if height else None
        except ValueError:
            height = None
        try:
            weight = float(weight) if weight else None
        except ValueError:
            weight = None

        record = VitalSignsRecord.objects.create(
            patient=patient,
            blood_pressure=blood_pressure,
            pulse_rate=pulse_rate,
            temperature=temperature,
            height=height,
            weight=weight
        )
        
        VitalSigns.objects.update_or_create(
            patient=patient,
            defaults={
                'blood_pressure': blood_pressure,
                'pulse_rate': pulse_rate,
                'temperature': temperature,
                'height': height,
                'weight': weight,
            }
        )
        
        return redirect('patient-detail', pk=patient.patientID)
    
    return render(request, 'patientInfo/vital_signs_create.html', {'patient': patient})


@login_required
@role_required(['BHW', 'DOCTOR'], 'Update vital signs record on the Patient Information')
def vital_signs_update(request, pk, vital_signs_id):
    patient = get_object_or_404(Patient, patientID=pk)
    record = get_object_or_404(VitalSignsRecord, id=vital_signs_id, patient=patient)
    
    if request.method == 'POST':
        blood_pressure = request.POST.get('blood_pressure')
        pulse_rate = request.POST.get('pulse_rate')
        temperature = request.POST.get('temperature')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        
        try:
            pulse_rate = int(pulse_rate) if pulse_rate else None
        except ValueError:
            pulse_rate = None
        try:
            temperature = float(temperature) if temperature else None
        except ValueError:
            temperature = None
        try:
            height = float(height) if height else None
        except ValueError:
            height = None
        try:
            weight = float(weight) if weight else None
        except ValueError:
            weight = None
        
        record.blood_pressure = blood_pressure
        record.pulse_rate = pulse_rate
        record.temperature = temperature
        record.height = height
        record.weight = weight
        record.save()

        # Update current VitalSigns if this is the latest record
        latest_record = VitalSignsRecord.objects.filter(patient=patient).order_by('-recorded_at').first()
        if latest_record and latest_record.id == record.id:
            VitalSigns.objects.update_or_create(
                patient=patient,
                defaults={
                    'blood_pressure': blood_pressure,
                    'pulse_rate': pulse_rate,
                    'temperature': temperature,
                    'height': height,
                    'weight': weight,
                }
            )

        # Create log entry for updating vital signs record
        now = datetime.now()
        formatted_date = now.strftime("%b. %d, %Y")
        formatted_time = now.strftime("%I:%M%p")
        Logs.objects.create(
            datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
            timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
            module="Vital Signs",
            action="Update Vital Signs Record",
            performed_to=f"Vital Signs Record ID - {record.id} for {patient.patientID}: {patient.resident.last_name}, {patient.resident.first_name}",
            performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
        )
        
        messages.success(request, "Vital signs record updated successfully!")
        return redirect('patient-detail', pk=patient.patientID)
    
    return render(request, 'patientInfo/vital_signs_update.html', {'patient': patient, 'record': record})



@login_required
@role_required(['ADMIN'], 'Delete vital signs record on the Patient Information')
def vital_signs_delete(request, pk, vital_signs_id):
    patient = get_object_or_404(Patient, patientID=pk)
    record = get_object_or_404(VitalSignsRecord, id=vital_signs_id, patient=patient)
    
    # Check if this record is the latest one
    latest_record = VitalSignsRecord.objects.filter(patient=patient).order_by('-recorded_at').first()
    if latest_record and latest_record.id == record.id:
        messages.warning(request, "You cannot delete the latest vital signs record.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    now = datetime.now()
    formatted_date = now.strftime("%b. %d, %Y")
    formatted_time = now.strftime("%I:%M%p")
    
    Logs.objects.create(
        datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
        timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
        module="Vital Signs",
        action="Delete Vital Signs Record",
        performed_to=f"Vital Signs Record ID - {record.id} for {patient.patientID}: {patient.resident.last_name}, {patient.resident.first_name}",
        performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
    )
    
    record.delete()
    messages.success(request, "Vital signs record deleted successfully!")
    return redirect(request.META.get('HTTP_REFERER', '/'))


# === PRESENT ILLNESS FUNCTIONALITY ===
@login_required
@role_required(['BHW', 'DOCTOR'], 'Create Present Illness on Patient Information')
def present_illness_create(request, patient_id):
    patient = get_object_or_404(Patient, patientID=patient_id)
    
    if request.method == "POST":
        illness_name = request.POST.get('illness_name', '').strip()
        start_date_str = request.POST.get('start_date', '').strip()
        treatment = request.POST.get('treatment', '').strip()
        
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None
        except ValueError:
            start_date = None
        
        # Create only if required fields are provided.
        if illness_name and start_date:
            PresentIllness.objects.create(
                patient=patient,
                illness_name=illness_name,
                start_date=start_date,
                treatment=treatment
            )
            messages.success(request, "Present illness record created successfully!")
            return redirect('patient-detail', pk=patient.patientID)
        else:
            messages.error(request, "Illness Name and Start Date are required.")
    
    return render(request, 'patientInfo/present_illness_create.html', {'patient': patient})

@login_required
@role_required(['BHW', 'DOCTOR'], 'Update Present Illness on Patient Information')
def present_illness_update(request, illness_id):
    present_illness = get_object_or_404(PresentIllness, id=illness_id)
    patient = present_illness.patient
    
    if request.method == "POST":
        illness_name = request.POST.get('illness_name', '').strip()
        start_date_str = request.POST.get('start_date', '').strip()
        treatment = request.POST.get('treatment', '').strip()
        
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None
        except ValueError:
            start_date = present_illness.start_date
        
        present_illness.illness_name = illness_name
        present_illness.start_date = start_date
        present_illness.treatment = treatment
        present_illness.save()

        # Create log entry for update
        now = datetime.now()
        formatted_date = now.strftime("%b. %d, %Y")
        formatted_time = now.strftime("%I:%M%p")
        Logs.objects.create(
            datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
            timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
            module="Present Illness",
            action="Update Present Illness Record",
            performed_to=f"Present Illness Record ID - {present_illness.id} for {patient.patientID}: {patient.resident.last_name}, {patient.resident.first_name}",
            performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
        )

        messages.success(request, "Present illness record updated successfully!")
        return redirect('patient-detail', pk=patient.patientID)
    
    return render(request, 'patientInfo/present_illness_update.html', {
        'present_illness': present_illness,
        'patient': patient,
    })


@login_required
@role_required(['ADMIN'], 'Delete Present Illness on Patient Information')
def present_illness_delete(request, illness_id):
    present_illness = get_object_or_404(PresentIllness, id=illness_id)
    patient = present_illness.patient

    now = datetime.now()
    formatted_date = now.strftime("%b. %d, %Y")
    formatted_time = now.strftime("%I:%M%p")

    Logs.objects.create(
        datelog=datetime.strptime(formatted_date, "%b. %d, %Y").date(),
        timelog=datetime.strptime(formatted_time, "%I:%M%p").time(),
        module="Present Illness",
        action="Delete Present Illness Record",
        performed_to=f"Present Illness Record ID - {present_illness.id} for {patient.patientID}: {patient.resident.last_name}, {patient.resident.first_name}",
        performed_by=f"username: {request.user.username} - {request.user.last_name}, {request.user.first_name}"
    )

    present_illness.delete()
    messages.success(request, "Present illness record deleted successfully!")
    return redirect(request.META.get('HTTP_REFERER', '/'))
