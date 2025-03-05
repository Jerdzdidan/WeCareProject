from django.urls import path
from . import views

urlpatterns = [
    path('select/', views.scheduled_checkup_patient_select, name='scheduled-checkup-patient-select'),
    path('create/<str:pk>/', views.scheduled_checkup_create, name='scheduled-checkup-create'),
]
