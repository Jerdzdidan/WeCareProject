from django.db import models

# Create your models here.
class Resident(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_initial = models.CharField(max_length=5)
    age = models.CharField(max_length=2)