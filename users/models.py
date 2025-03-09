from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('BHW', 'Barangay Health Worker'),
        ('BRGY-STAFF', 'Barangay Staff'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'Admin'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    userrole = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='BHW')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='ACTIVE')
    created_by = models.ForeignKey(User, related_name='created_user_profiles', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.userrole == 'ADMIN':
            self.user.is_staff = True  
            self.user.is_superuser = True  
        else:
            self.user.is_staff = False
            self.user.is_superuser = False

        self.user.save()  
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username}: {self.userrole}'
