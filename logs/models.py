from django.db import models

# Create your models here.
class Logs(models.Model):
    datelog = models.DateField()
    timelog = models.TimeField()
    module = models.CharField(max_length=20)
    action = models.CharField(max_length=20)
    performed_to = models.CharField(max_length=20)
    performed_by = models.CharField(max_length=20)