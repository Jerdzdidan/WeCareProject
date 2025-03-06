from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, date
from scheduledcheckup.models import ScheduledCheckup
from patientInfo.models import Patient

# Create your views here.

@login_required
def scheduled_checkup_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%b %d, %Y").date()
            end_date_obj = datetime.strptime(end_date, "%b %d, %Y").date()
            scheduled_checkups = ScheduledCheckup.objects.filter(
                checkup_date__range=[start_date_obj, end_date_obj]
            ).order_by("checkup_date")
        except ValueError:
            scheduled_checkups = ScheduledCheckup.objects.none()
    elif start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%b %d, %Y").date()
            scheduled_checkups = ScheduledCheckup.objects.filter(
                checkup_date__gte=start_date_obj
            ).order_by("checkup_date")
        except ValueError:
            scheduled_checkups = ScheduledCheckup.objects.none()
    elif end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%b %d, %Y").date()
            scheduled_checkups = ScheduledCheckup.objects.filter(
                checkup_date__lte=end_date_obj
            ).order_by("checkup_date")
        except ValueError:
            scheduled_checkups = ScheduledCheckup.objects.none()
    else:
        scheduled_checkups = ScheduledCheckup.objects.none()

    context = {
        "scheduled_checkups": scheduled_checkups,
    }
    return render(request, "scheduledcheckup/scheduled_checkup_list.html", context)

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
        return redirect("scheduled-checkup-list")
    
    context = {
        "patient": patient,
    }
    return render(request, "scheduledcheckup/scheduled_checkup_create.html", context)

@login_required
def scheduled_checkup_update(request, checkup_id):
    checkup = get_object_or_404(ScheduledCheckup, id=checkup_id)
    
    if request.method == "POST":
        checkup_date_str = request.POST.get("checkup_date", "").strip()
        checkup_time_str = request.POST.get("checkup_time", "").strip()
        notes = request.POST.get("notes", "").strip()
        
        try:
            # Expecting a date format "Y-m-d"
            checkup_date = datetime.strptime(checkup_date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid checkup date format. Please use YYYY-MM-DD.")
            return redirect("scheduled-checkup-update", checkup_id=checkup.id)
        
        if checkup_time_str:
            try:
                # Expecting time format "H:i" for 24-hr or "I:M p" for 12-hr; adjust accordingly
                # For our case we assume "H:i" format if using flatpickr with time
                checkup_time = datetime.strptime(checkup_time_str, "%H:%M").time()
            except ValueError:
                messages.error(request, "Invalid checkup time format. Please use HH:MM (24-hour) or adjust as needed.")
                return redirect("scheduled-checkup-update", checkup_id=checkup.id)
        else:
            checkup_time = None

        checkup.checkup_date = checkup_date
        checkup.checkup_time = checkup_time
        checkup.notes = notes
        checkup.save()

        messages.success(request, "Scheduled checkup updated successfully!")
        return redirect("scheduled-checkup-list")
    
    context = {
        "checkup": checkup,
    }
    return render(request, "scheduledcheckup/scheduled_checkup_update.html", context)

@login_required
def scheduled_checkup_delete(request, checkup_id):
    checkup = get_object_or_404(ScheduledCheckup, id=checkup_id)

    checkup.delete()
    messages.success(request, "Scheduled checkup deleted successfully!")
    return redirect("scheduled-checkup-list")