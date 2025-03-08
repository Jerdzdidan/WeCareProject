from django.shortcuts import render
from residentInfo.models import Resident
from dateutil.relativedelta import relativedelta

# Create your views here.
def residentInfoReport(request):
    category = request.GET.get('category', '')
    gender = request.GET.get('gender', '')
    age_group = request.GET.get('age', '')

    residents = Resident.objects.select_related('family').all()

    if category:
        residents = residents.filter(category=category)
    if gender:
        residents = residents.filter(gender=gender)
    
    if age_group:
        try:
            age_group = int(age_group)
        except ValueError:
            age_group = None
        
        if age_group is not None:
            if age_group == 6:
                residents = residents.filter(age__lte=6)
            elif age_group == 18:
                residents = residents.filter(age__gte=7, age__lte=18)
            elif age_group == 59:
                residents = residents.filter(age__gte=19, age__lte=59)
            elif age_group == 150:
                residents = residents.filter(age__gte=60)

    residents = residents.order_by('family__family_no', 'id')

    return render(request, 'reports/residentInfoReport.html', {'residents': residents})
