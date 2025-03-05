from django.db import models
from patientInfo.models import Patient 

# Create your models here.

class ScheduledCheckup(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='scheduled_checkups')
    checkup_date = models.DateField()
    checkup_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Checkup for {self.patient.patientID} on {self.checkup_date}"
