from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone
from patientInfo.models import (
    Patient,
    VitalSigns,
    Vaccination,
    PastMedicalHistory,
    MedicalRecord,
    PresentIllness,
    MedicineTracking
)
from residentInfo.models import Resident

# === PATIENT RECORD FUNCTIONALITY ===
@login_required
def patient_list(request):
    patients = Patient.objects.select_related('resident').all().order_by('patientID')
    return render(request, 'patientInfo/patient_list.html', {'patients': patients})

@login_required
def patient_select(request):
    available_residents = Resident.objects.filter(patient__isnull=True).order_by('id')
    return render(request, 'patientInfo/patient_select.html', {'available_residents': available_residents})

@login_required
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
        
        index = 0
        while True:
            illness_key = f"present_illness[{index}][illness_name]"
            if illness_key in request.POST:
                illness_name = request.POST.get(illness_key, "").strip()
                start_date_str = request.POST.get(f"present_illness[{index}][start_date]", "").strip()
                end_date_str = request.POST.get(f"present_illness[{index}][end_date]", "").strip()
                treatment = request.POST.get(f"present_illness[{index}][treatment]", "").strip()
                try:
                    start_date = datetime.strptime(start_date_str, "%b %d, %Y").date() if start_date_str else None
                except ValueError:
                    start_date = None
                try:
                    end_date = datetime.strptime(end_date_str, "%b %d, %Y").date() if end_date_str else None
                except ValueError:
                    end_date = None
                if illness_name and start_date:
                    patient.present_illnesses.create(
                        illness_name=illness_name,
                        start_date=start_date,
                        end_date=end_date,
                        treatment=treatment
                    )
                index += 1
            else:
                break
        
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
            allergy_details=allergy_details
        )
        
        MedicalRecord.objects.create(
            patient=patient,
            concern="Initial Check-Up",
            description="Auto-generated record on patient creation.",
            last_visited=datetime.today().date()
        )
        
        messages.success(request, "Patient record created successfully!")
        return redirect('patient-list')
    
    return render(request, 'patientInfo/patient_create_details.html', {'resident': resident})

@login_required
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
        
        if vital_signs:
            vital_signs.blood_pressure = bp or None
            vital_signs.pulse_rate = pr or None
            vital_signs.temperature = temp or None
            vital_signs.height = height or None
            vital_signs.weight = weight or None
            vital_signs.save()
        else:
            if any([bp, pr, temp, height, weight]):
                VitalSigns.objects.create(
                    patient=patient,
                    blood_pressure=bp or None,
                    pulse_rate=pr or None,
                    temperature=temp or None,
                    height=height or None,
                    weight=weight or None,
                )
                
        patient.present_illnesses.all().delete()
        index = 0
        while True:
            illness_key = f"present_illness[{index}][illness_name]"
            if illness_key in request.POST:
                illness_name = request.POST.get(illness_key, "").strip()
                start_date_str = request.POST.get(f"present_illness[{index}][start_date]", "").strip()
                end_date_str = request.POST.get(f"present_illness[{index}][end_date]", "").strip()
                treatment = request.POST.get(f"present_illness[{index}][treatment]", "").strip()
                try:
                    start_date = datetime.strptime(start_date_str, "%b %d, %Y").date() if start_date_str else None
                except ValueError:
                    start_date = None
                try:
                    end_date = datetime.strptime(end_date_str, "%b %d, %Y").date() if end_date_str else None
                except ValueError:
                    end_date = None
                if illness_name and start_date:
                    patient.present_illnesses.create(
                        illness_name=illness_name,
                        start_date=start_date,
                        end_date=end_date,
                        treatment=treatment
                    )
                index += 1
            else:
                break
        
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
                    allergy_details=allergy_details
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
def patient_delete_confirm(request, pk):
    patient = get_object_or_404(Patient, patientID=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, "Patient record deleted successfully!")
        return redirect('patient-list')
    
    return render(request, 'patientInfo/patient_delete.html', {'patient': patient})

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, patientID=pk)
    records = patient.medical_records.all().order_by('-last_visited')
    
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
    return render(request, 'patientInfo/patient_detail.html', {
        'patient': patient,
        'medical_records': records,
        'medicine_trackings': medicine_trackings,
    })


# === MEDICAL RECORD FUNCTIONALITY ===
@login_required
def medical_record_create(request, pk):
    patient = get_object_or_404(Patient, patientID=pk)
    if request.method == "POST":
        concern = request.POST.get('concern', '').strip()
        description = request.POST.get('description', '').strip()
        
        last_visited = datetime.today().date()
        MedicalRecord.objects.create(
            patient=patient,
            concern=concern,
            description=description,
            last_visited=last_visited
        )
        messages.success(request, "Medical record created successfully!")
        return redirect('patient-detail', pk=patient.patientID)
    return render(request, 'patientInfo/medical_record_create.html', {'patient': patient})


@login_required
def medical_record_list(request, pk):
    patient = get_object_or_404(Patient, patientID=pk)
    records = patient.medical_records.all().order_by('-last_visited')
    filter_date = request.GET.get('filter_date', '')
    if filter_date:
        try:
            filter_date_obj = datetime.strptime(filter_date, "%Y-%m-%d").date()
            records = records.filter(last_visited=filter_date_obj)
        except ValueError:
            pass
    return render(request, 'patientInfo/medical_record_list.html', {
        'patient': patient,
        'medical_records': records,
        'filter_date': filter_date,
    })

@login_required
def medical_record_update(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    if request.method == "POST":
        concern = request.POST.get('concern', '').strip()
        description = request.POST.get('description', '').strip()
        last_visited_str = request.POST.get('last_visited', '').strip()
        try:
            last_visited = datetime.strptime(last_visited_str, "%Y-%m-%d").date()
        except ValueError:
            last_visited = record.last_visited
        record.concern = concern
        record.description = description
        record.last_visited = last_visited
        record.save()
        messages.success(request, "Medical record updated successfully!")
        return redirect('patient-detail', pk=record.patient.patientID)
    return render(request, 'patientInfo/medical_record_update.html', {'record': record})

@login_required
def medical_record_delete(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    if request.method == 'POST':
        patientID = record.patient.patientID
        record.delete()
        messages.success(request, "Medical record deleted successfully!")
        return redirect('patient-detail', pk=patientID)
    return render(request, 'patientInfo/medical_record_delete.html', {'record': record})

@login_required
def medicine_tracking_create(request, pk):
    patient = get_object_or_404(Patient, patientID=pk)
    if request.method == "POST":
        medicine_name = request.POST.get('medicine_name', '').strip()
        dosage = request.POST.get('dosage', '').strip()
        frequency = request.POST.get('frequency', '').strip()
        start_date_str = request.POST.get('start_date', '').strip()
        end_date_str = request.POST.get('end_date', '').strip()
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            start_date = None
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
        except ValueError:
            end_date = None

        MedicineTracking.objects.create(
            patient=patient,
            medicine_name=medicine_name,
            dosage=dosage,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date
        )
        messages.success(request, "Medicine tracking record created successfully!")
        return redirect('patient-detail', pk=patient.patientID)
    return render(request, 'patientInfo/medicine_tracking_create.html', {'patient': patient})
