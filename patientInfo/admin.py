from django.contrib import admin

from .models import (
    Patient,
    VitalSigns,
    PresentIllness,
    Vaccination,
    PastMedicalHistory,
    MedicalRecord,
    MedicineTracking,
    VitalSignsRecord
)

admin.site.register(Patient)
admin.site.register(VitalSigns)
admin.site.register(PresentIllness)
admin.site.register(Vaccination)
admin.site.register(PastMedicalHistory)
admin.site.register(MedicalRecord)
admin.site.register(MedicineTracking)
admin.site.register(VitalSignsRecord)