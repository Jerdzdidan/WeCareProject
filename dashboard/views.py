from django.shortcuts import render
from residentInfo.models import Resident, Family
from patientInfo.models import Patient
from django.contrib.auth.decorators import login_required
from users.decorators import role_required

@login_required
@role_required(['ADMIN', 'BRGY-STAFF', 'BHW', 'DOCTOR'], 'Dashboard')
def dashboard(request):
    residents = Resident.objects.all()
    patients = Patient.objects.all()

    # Resident Count
    residentCount_total = residents.count()
    residentCount_na = residents.filter(category='N/A').count()
    residentCount_pwd = residents.filter(category='PWD').count()
    residentCount_solo_parent = residents.filter(category='Solo Parent').count()
    residentCount_children = residents.filter(category='Children').count()
    residentCount_senior = residents.filter(category='Senior').count()
    residentCount_pregnant = residents.filter(category='Pregnant').count()
    residentCount_male = residents.filter(gender='Male').count()
    residentCount_female = residents.filter(gender='Female').count()
    residentCount_other = residents.filter(gender='Other').count()

    # Patient Count by Age Groups 
    patientCount_total = patients.count()
    patientCount_0_6 = patients.filter(resident__age__gte=0, resident__age__lt=6).count()
    patientCount_6_18 = patients.filter(resident__age__gte=6, resident__age__lt=18).count()
    patientCount_19_59 = patients.filter(resident__age__gte=19, resident__age__lt=59).count()
    patientCount_59_above = patients.filter(resident__age__gte=59).count()
    # Patient Count by Category
    patientCount_na = patients.filter(resident__category='N/A').count()
    patientCount_senior = patients.filter(resident__category='Senior').count()
    patientCount_pwd = patients.filter(resident__category='PWD').count()
    patientCount_solo_parent = patients.filter(resident__category='Solo Parent').count()
    patientCount_pregnant = patients.filter(resident__category='Pregnant').count()
    # Patient Count by Gender
    patientCount_male = patients.filter(resident__category='Male').count()
    patientCount_female = patients.filter(resident__category='Female').count()
    patientCount_other = patients.filter(resident__category='Other').count()

    context = {
        # Resident Counts
        'residentCount_total': residentCount_total,
        'residentCount_na': residentCount_na,
        'residentCount_pwd': residentCount_pwd,
        'residentCount_solo_parent': residentCount_solo_parent,
        'residentCount_children': residentCount_children,
        'residentCount_senior': residentCount_senior,
        'residentCount_pregnant': residentCount_pregnant,
        'residentCount_male': residentCount_male,
        'residentCount_female': residentCount_female,
        'residentCount_other': residentCount_other,
        # Patient Counts by Age Groups
        'patientCount_total': patientCount_total,
        'patientCount_0_6': patientCount_0_6,
        'patientCount_6_18': patientCount_6_18,
        'patientCount_19_59': patientCount_19_59,
        'patientCount_59_above': patientCount_59_above,
        # Patient Counts by Category
        'patientCount_na': patientCount_na,
        'patientCount_senior': patientCount_senior,
        'patientCount_pwd': patientCount_pwd,
        'patientCount_solo_parent': patientCount_solo_parent,
        'patientCount_pregnant': patientCount_pregnant,
        # Patient Count by Gender
        'patientCount_male': patientCount_male,
        'patientCount_female': patientCount_female,
        'patientCount_other': patientCount_other,
    }

    return render(request, 'dashboard/dashboard.html', context)
