from django.shortcuts import render
from .models import UserProfile

# Create your views here.
def accountlist(request):
    profiles = UserProfile.objects.all()
    return render(request, 'users/account_list.html', {'profiles': profiles})

