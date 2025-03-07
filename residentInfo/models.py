from django.db import models, transaction, connection
import datetime
from django.utils import timezone
import re

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
)

CATEGORY_CHOICES = (
    ('N/A', 'N/A'),
    ('PWD', 'PWD'),
    ('Senior', 'Senior'),
    ('Children', 'Children'),
    ('Solo Parent', 'Solo Parent'),
    ('Pregnant', 'Pregnant'),
)

class Family(models.Model):
    family_no = models.CharField(max_length=10, primary_key=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.family_no:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT MAX(CAST(SUBSTR(family_no, 2) AS INTEGER)) "
                        "FROM residentInfo_family "
                        "WHERE family_no LIKE 'F%'"
                    )
                    max_number_row = cursor.fetchone()
                    max_number = max_number_row[0] or 0 if max_number_row[0] is not None else 0
                    
                new_number = max_number + 1
                self.family_no = f"F{new_number}"
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Family #{self.family_no}"


class Resident(models.Model):
    id = models.CharField(max_length=10, primary_key=True, editable=False)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='residents', null=True)
    
    last_name = models.CharField(max_length=100, default="--")
    first_name = models.CharField(max_length=100, default="--")
    middle_name = models.CharField(max_length=100, blank=True, null=True, default="--")
    
    relationship_to_head = models.CharField(max_length=50, default="--")
    
    birthdate = models.DateField(default=datetime.date(2000, 1, 1))
    
    age = models.PositiveIntegerField(default=0)
    
    civil_status = models.CharField(max_length=50, default="--")
    
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="Male")
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='N/A')
    
    present_address = models.CharField(max_length=255, default="--")
    contact_number = models.CharField(max_length=20, default="--")
    
    date_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT MAX(CAST(SUBSTR(id, 2) AS INTEGER)) FROM residentInfo_resident WHERE id LIKE 'R%'"
                    )
                    max_number_row = cursor.fetchone()
                    max_number = max_number_row[0] or 0 if max_number_row[0] is not None else 0
                new_number = max_number + 1
                self.id = f"R{new_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.last_name}, {self.first_name}"
