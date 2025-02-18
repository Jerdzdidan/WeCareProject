from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import AccountForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout

@login_required
def accountlist(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have perimission to see accounts list.")
    accounts = UserProfile.objects.all()
    return render(request, 'users/account_list.html', {'accounts': accounts})

@login_required
def accountCreate(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permissions to create accounts.")
    
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.warning(request, "Username already exists. Please choose a different one.")
                return redirect('account-create')
            
            profile = form.save(commit=False, created_by=request.user)
            profile.save()
            
            messages.success(request, "Account created successfully!")
            return redirect('account-list')
    else:
        form = AccountForm()

    return render(request, 'users/create.html', {'form': form})


@login_required
def accountUpdate(request, pk):
    if request.user.userprofile.usertype != 'Admin':
        return HttpResponseForbidden()

    account = get_object_or_404(UserProfile, pk=pk)

    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)  
        if form.is_valid():
            form.save()
            return redirect('account-list')  
    else:
        form = AccountForm(instance=account)  

    return render(request, 'users/update.html', {'form': form})


@login_required
def accountDeleteConfirm(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to delete accounts.")
    
    account = get_object_or_404(UserProfile, pk=pk)
    
    if request.user == account.user:
        messages.warning(request, "You cannot delete your own account.")
        return redirect('account-list')
    
    if request.method == 'POST':
        account.user.delete() 
        account.delete()
        
        return redirect('account-list')

    return render(request, 'users/delete_confirm.html', {'account': account})

# Custom view for logging out.
def custom_logout(request):
    logout(request)
    return render(request, 'users/logout.html')