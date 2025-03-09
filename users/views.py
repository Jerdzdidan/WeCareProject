from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .models import UserProfile
from .forms import AccountForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate

@login_required
@role_required(['ADMIN'], 'User Management')
def accountlist(request):
    accounts = UserProfile.objects.all()
    return render(request, 'users/account_list.html', {'accounts': accounts})

@login_required
@role_required(['ADMIN'], 'Account Creation in User Management')
def accountCreate(request):

    context = {}
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        userrole = request.POST.get('userrole', '')

        context.update({
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'email': email,
            'userrole': userrole
        })

        errors = False

        if not all([first_name, last_name, username, password1, password2, userrole]):
            context['error_message'] = "All fields are required."
            errors = True

        if password1 != password2:
            context['password_error'] = "Passwords do not match."
            errors = True

        if User.objects.filter(username=username).exists():
            context['username_error'] = "Username already exists."
            errors = True

        if not errors:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )

                UserProfile.objects.create(
                    user=user,
                    userrole=userrole,
                    created_by=request.user
                )

                messages.success(request, "Account created successfully!")
                return redirect('account-list')

            except Exception as e:
                context['error_message'] = f"Error creating account: {str(e)}"

    return render(request, 'users/create.html', context)


@login_required
@role_required(['ADMIN'], 'Account Update in User Management')
def accountUpdate(request, pk):

    profile = get_object_or_404(UserProfile, pk=pk)
    user = profile.user
    context = {
        'user': user,
        'profile': profile
    }

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        userrole = request.POST.get('userrole', 'BHW')
        status = request.POST.get('status', 'ACTIVE')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = False
        context.update({
            'email': email,
            'userrole': userrole,
            'status': status
        })

        if not all([userrole, status]):
            context['error_message'] = "All required fields must be filled."
            errors = True

        if password1 or password2:
            if not (password1 and password2):
                context['password_error'] = "Both password fields must be filled."
                errors = True
            elif password1 != password2:
                context['password_error'] = "Passwords do not match."
                errors = True

        if not errors:
            try:
                user.email = email
                
                if password1:
                    user.set_password(password1)
                
                user.save()

                profile.userrole = userrole
                profile.status = status
                profile.save()

                messages.success(request, "Account updated successfully!")
                return redirect('account-list')
            except Exception as e:
                context['error_message'] = f"Error updating account: {str(e)}"
        else:
            context['error_message'] = "Please correct the errors below."

    return render(request, 'users/update.html', context)


@login_required
@role_required(['ADMIN'], 'Account Deletion in User Management')
def accountDeleteConfirm(request, pk):
    
    account = get_object_or_404(UserProfile, pk=pk)
    
    if request.user == account.user:
        messages.warning(request, "You cannot delete your own account.")
        return redirect('account-list')
    
    try:
        username = account.user.username
        account.user.delete()
        account.delete()
        
        messages.success(request, f"Account '{username}' deleted successfully!")
    except Exception as e:
        messages.error(request, f"Error deleting account: {str(e)}")

    return redirect('account-list')

def custom_logout(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out!")
    return redirect("login")

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        user_profile = UserProfile.objects.filter(user=user).first()
        if user_profile is not None and user_profile.status == 'INACTIVE':
            messages.error(request, "Your account is INACTIVE. Please contact the administrator for the reactivation of your account.")
            return render(request, "users/login.html")

        elif user is not None:
            login(request, user)
            return redirect("home") 
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "users/login.html")