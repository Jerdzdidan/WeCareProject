from django.shortcuts import render
from .models import Logs
from users.decorators import role_required
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
@role_required(['ADMIN'], 'Logs')
def logs_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    logs = Logs.objects.all()

    if start_date and end_date:
        logs = logs.filter(datelog__range=[start_date, end_date])
    elif start_date:
        logs = logs.filter(datelog__gte=start_date)
    elif end_date:
        logs = logs.filter(datelog__lte=end_date)

    return render(request, 'logs/logs_list.html', {'logs': logs})
