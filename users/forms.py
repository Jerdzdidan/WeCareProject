from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class AccountForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Username")
    email = forms.EmailField(required=False, label="Email")
    first_name = forms.CharField(max_length=30, required=False, label="First Name")
    last_name = forms.CharField(max_length=30, required=False, label="Last Name")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password", required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Retype Password", required=False)

    class Meta:
        model = UserProfile
        fields = [
            'username',
            'password1',
            'password2',
            'email',
            'first_name',
            'last_name',
            'userrole',
            'status',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['password1'].widget.attrs['placeholder'] = 'Leave blank to keep unchanged'
            self.fields['password2'].widget.attrs['placeholder'] = 'Leave blank to keep unchanged'

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if (password1 or password2) and password1 != password2:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

    def save(self, commit=True, created_by=None):
        user_profile = super().save(commit=False)
        if not hasattr(user_profile, 'user') or user_profile.user is None:
            user = User()
            user_profile.user = user
        else:
            user = user_profile.user

        user.username = self.cleaned_data.get('username')
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)

        if commit:
            user.save()
            user_profile.created_by = created_by
            user_profile.save()
        return user_profile
