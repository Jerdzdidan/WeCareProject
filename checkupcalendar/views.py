from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from scheduledcheckup.models import ScheduledCheckup
import json
from django.http import JsonResponse

@login_required
def calendar_view(request):
    events_qs = ScheduledCheckup.objects.values('checkup_date').annotate(count=Count('id')).order_by('checkup_date')
    
    events = [
        {
            'title': "3 scheduled (TEST)",
            'start': "2024-01-01",
            'url': "/scheduled-checkup/?start_date=Jan 01, 2024&end_date=Jan 01, 2024"
        }
    ]
    
    for event in events_qs:
        d = event['checkup_date']
        count = event['count']
        formatted_date = d.strftime("%b %d, %Y")  
        url = f"/scheduled-checkup/?start_date={formatted_date}&end_date={formatted_date}"
        events.append({
            'title': f"{count} scheduled",
            'start': d.isoformat(),  
            'url': url,
        })
        
    context = {
        'events': json.dumps(events),  
    }
    return render(request, "checkupcalendar/calendar.html", context)
