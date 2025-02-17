from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import UserProfile  
# from .forms import AccountForm  

@login_required
def accountlist(request):
    if request.user.usertype != 'admin':
        return HttpResponseForbidden()
    accounts = UserProfile.objects.all()
    return render(request, 'accounts/list.html', {'accounts': accounts})

@login_required
def accountCreate(request):
    if request.user.usertype != 'admin':
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('account-list')
    else:
        form = AccountForm()
    return render(request, 'accounts/create.html', {'form': form})

@login_required
def accountUpdate(request):
    if request.user.usertype != 'admin':
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        account = get_object_or_404(UserProfile, pk=account_id)
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect('account-list')
    else:
        form = AccountForm()
    return render(request, 'accounts/update.html', {'form': form})

@login_required
def accountDelete(request, pk):
    if request.user.usertype != 'admin':
        return HttpResponseForbidden()
    
    account = get_object_or_404(UserProfile, pk=pk)
    if request.method == 'POST':
        account.delete()
        return redirect('account-list')
    return redirect('account-delete-confirm', pk=pk)

@login_required
def accountDeleteConfirm(request, pk):
    if request.user.usertype != 'admin':
        return HttpResponseForbidden()
    
    account = get_object_or_404(UserProfile, pk=pk)
    return render(request, 'accounts/delete_confirm.html', {'account': account})