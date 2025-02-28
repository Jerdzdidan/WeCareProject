from django.contrib import admin
from .models import Medicine, MedicineStock

# Register your models here.
admin.site.register(Medicine)
admin.site.register(MedicineStock)