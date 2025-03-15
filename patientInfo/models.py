from django.db import models, transaction
from residentInfo.models import Resident  
from medicineMonitoring.models import Medicine, MedicineStock
from datetime import datetime, date
from decimal import Decimal


class Patient(models.Model):
    patientID = models.CharField(max_length=10, unique=True, editable=False, default="P0")
    resident = models.OneToOneField(Resident, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.patientID or self.patientID == "P0":
            with transaction.atomic():
                last_patient = Patient.objects.select_for_update().order_by('-id').first()
                last_number = last_patient.id if last_patient else 0
                self.patientID = f"P{last_number + 1}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Patient {self.patientID} - {self.resident.first_name} {self.resident.last_name}"

    @property
    def last_visit_date(self):
        latest_record = self.medical_records.order_by('-last_visited').first()
        return latest_record.last_visited if latest_record else None


class VitalSigns(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name="vital_signs")
    blood_pressure = models.CharField(max_length=10, null=True, blank=True)  
    pulse_rate = models.IntegerField(null=True, blank=True) 
    temperature = models.FloatField(null=True, blank=True)  
    height = models.FloatField(null=True, blank=True)  
    weight = models.FloatField(null=True, blank=True) 

    def __str__(self):
        return f"Vital Signs for {self.patient.resident.first_name}"
    
class VitalSignsRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="vital_signs_records")
    blood_pressure = models.CharField(max_length=10, null=True, blank=True)
    pulse_rate = models.IntegerField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vital Signs Record for {self.patient.patientID} on {self.recorded_at:%b %d, %Y %H:%M}"

class PresentIllness(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="present_illnesses")
    illness_name = models.CharField(max_length=100)
    start_date = models.DateField()
    treatment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.illness_name} ({self.patient.resident.first_name})"

class Vaccination(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name="vaccinations")
    
    hepatitis_a = models.BooleanField(default=False)
    hepatitis_b = models.BooleanField(default=False)
    hpv_vaccine = models.BooleanField(default=False)
    pre_announced_vaccine = models.BooleanField(default=False)
    typhoid = models.BooleanField(default=False)
    mmr = models.BooleanField(default=False)
    dpt = models.BooleanField(default=False)
    chicken_pox = models.BooleanField(default=False)
    tetanus_toxoid = models.BooleanField(default=False)
    others = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Vaccinations for {self.patient.resident.first_name}"

class PastMedicalHistory(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name="past_medical_history")

    asthma = models.BooleanField(default=False)
    anemia = models.BooleanField(default=False)
    bad_teeth = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    depression = models.BooleanField(default=False)
    heart_disease = models.BooleanField(default=False)
    hearing_problem = models.BooleanField(default=False)
    high_blood_pressure = models.BooleanField(default=False)
    heart_attack = models.BooleanField(default=False)
    drug_allergy = models.BooleanField(default=False)
    allergy_details = models.TextField(null=True, blank=True)
    others = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Medical History for {self.patient.resident.first_name}"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medical_records")
    concern = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    last_visited = models.DateField() 

    def __str__(self):
        return f"Record for {self.patient.patientID} on {self.last_visited:%b %d, %Y}"


class MedicineTracking(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medicine_trackings")
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="medicine_trackings", null=True, blank=True)
    medicine_stock = models.ForeignKey(MedicineStock, on_delete=models.SET_NULL, null=True, blank=True)
    quantity_used = models.PositiveIntegerField(null=True)
    total_dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(null=True, blank=True)
    chief_complain = models.TextField(blank=True, null=True)
    date_given = models.DateField(default=date.today)
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"{self.medicine.medicine_name} for {self.patient.patientID} ({self.quantity_used} units)"