from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class AccountForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Username")
    email = forms.EmailField(required=False, label="Email")
    first_name = forms.CharField(max_length=30, required=False, label="First Name")
    last_name = forms.CharField(max_length=30, required=False, label="Last Name")

    password1 = forms.CharField(
        widget=forms.PasswordInput, label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Retype Password"
    )

    class Meta:
        model = UserProfile
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'usertype', 'status']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match!")

        return cleaned_data

    def save(self, commit=True, created_by=None):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data.get('email', ''),
            first_name=self.cleaned_data.get('first_name', ''),
            last_name=self.cleaned_data.get('last_name', '')
        )

        if self.cleaned_data['usertype'] == 'Admin':
            user.is_staff = True  
            user.is_superuser = True
            user.save()

        user_profile = super().save(commit=False)
        user_profile.user = user

        if created_by and created_by.is_staff:
            user_profile.created_by = created_by

        if commit:
            user_profile.save()

        return user_profile
