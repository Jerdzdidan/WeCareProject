from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from scheduledcheckup.models import ScheduledCheckup
from patientInfo.models import Patient

# Create your views here.

@login_required
def scheduled_checkup_patient_select(request):
    available_patients = Patient.objects.all().order_by('patientID')
    context = {
        'available_patients': available_patients,
    }
    return render(request, 'scheduledcheckup/patient_select.html', context)


@login_required
def scheduled_checkup_create(request, pk):
    patient = get_object_or_404(Patient, patientID=pk)
    if request.method == "POST":
        checkup_date_str = request.POST.get("checkup_date", "").strip()
        checkup_time_str = request.POST.get("checkup_time", "").strip()
        notes = request.POST.get("notes", "").strip()
        
        try:
            checkup_date = datetime.strptime(checkup_date_str, "%Y-%m-%d").date() if checkup_date_str else None
        except ValueError:
            checkup_date = None

        if not checkup_date:
            messages.error(request, "Please provide a valid checkup date.")
            return redirect("scheduled-checkup-create", pk=patient.patientID)
        
        if checkup_time_str:
            try:
                checkup_time = datetime.strptime(checkup_time_str, "%H:%M").time()
            except ValueError:
                checkup_time = None
        else:
            checkup_time = None

        ScheduledCheckup.objects.create(
            patient=patient,
            checkup_date=checkup_date,
            checkup_time=checkup_time,
            notes=notes,
        )
        messages.success(request, "Scheduled checkup created successfully!")
        return redirect("patient-detail", pk=patient.patientID)
    
    context = {
        "patient": patient,
    }
    return render(request, "scheduledcheckup/scheduled_checkup_create.html", context)
