from django.db import models, transaction
import datetime

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)

CATEGORY_CHOICES = (
    ('N/A', 'N/A'),
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
                last_family = Family.objects.select_for_update().order_by('-family_no').first()
                last_number = 0
                if last_family:
                    last_family_no = str(last_family.family_no)
                    if last_family_no.startswith('F'):
                        try:
                            last_number = int(last_family_no[1:])
                        except ValueError:
                            last_number = 0
                    else:
                        try:
                            last_number = int(last_family_no)
                        except ValueError:
                            last_number = 0
                new_number = last_number + 1
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
                last_resident = Resident.objects.select_for_update().order_by('-id').first()
                last_number = 0
                if last_resident:
                    last_id = str(last_resident.id)
                    if last_id.startswith('R'):
                        try:
                            last_number = int(last_id[1:])
                        except ValueError:
                            last_number = 0
                    else:
                        try:
                            last_number = int(last_id)
                        except ValueError:
                            last_number = 0
                new_number = last_number + 1
                self.id = f"R{new_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.last_name}, {self.first_name}"
