from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile

def role_required(allowed_roles, module_name):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            try:
                profile = request.user.userprofile
                if profile.userrole in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.warning(
                        request, 
                        f"You don't have permission to access the {module_name} module."
                    )
                    return redirect('home')
            except UserProfile.DoesNotExist:
                messages.warning(
                    request,
                    f"Complete your profile to access the {module_name} module."
                )
                return redirect('home')
        return wrapper
    return decorator