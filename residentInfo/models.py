from django.db import models
import datetime

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)

CATEGORY_CHOICES = (
    ('NA', 'N/A'),
    ('Senior', 'Senior'),
    ('Children', 'Children'),
    ('Solo Parent', 'Solo Parent'),
    ('Pregnant', 'Pregnant'),
)

class Family(models.Model):
    family_no = models.AutoField(primary_key=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Family #{self.family_no}"
    
    @property
    def head(self):
        return self.residents.filter(relationship_to_head="Head of the family").first()


class Resident(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='residents', null=True)
    
    last_name = models.CharField(max_length=100, default="--")
    first_name = models.CharField(max_length=100, default="--")
    middle_name = models.CharField(max_length=100, blank=True, null=True, default="--")
    
    relationship_to_head = models.CharField(max_length=50, default="--")
    
    birthdate = models.DateField(default=datetime.date(2000, 1, 1))
    
    age = models.PositiveIntegerField(default=0)
    
    civil_status = models.CharField(max_length=50, default="--")
    
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="Male")
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='NA')
    
    present_address = models.CharField(max_length=255, default="--")
    contact_number = models.CharField(max_length=20, default="--")
    
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
