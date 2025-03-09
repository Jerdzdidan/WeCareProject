from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class AccountForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    userrole = forms.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES)
    status = forms.ChoiceField(choices=UserProfile.STATUS_CHOICES)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'userrole', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        user = self.instance.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.save()
        
        profile = super().save(commit=False)
        profile.userrole = self.cleaned_data['userrole']
        profile.status = self.cleaned_data['status']
        
        if commit:
            profile.save()
        return profile