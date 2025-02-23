from django.shortcuts import render
from residentInfo.models import Resident, Family

# Create your views here.
def dashboard(request):
    residents = Resident.objects.all()

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

    context = {
        # Resident Count
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
    }

    return render(request, 'dashboard/dashboard.html', context)