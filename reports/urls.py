from django.urls import path
from . import views

urlpatterns = [
    path('residentInfo/', views.residentInfoReport, name='reports-resident-info'),
    path('residentInfo/export/xlsx/', views.resident_export_xlsx, name='resident-export-xlsx'),
    path('residentInfo/export/pdf/', views.resident_export_pdf, name='resident-export-pdf'),

    path('patientInfo/', views.patientInfoReport, name='reports-patient-info'),
    path('patientInfo/export/xlsx/', views.patient_export_xlsx, name='patient-export-xlsx'),
    path('patientInfo/export/pdf/', views.patient_export_pdf, name='patient-export-pdf'),
]
