from django.urls import path
from . import views

urlpatterns = [
    path('', views.scheduled_checkup_list, name='scheduled-checkup-list'),
    path('select/', views.scheduled_checkup_patient_select, name='scheduled-checkup-patient-select'),
    path('create/<str:pk>/', views.scheduled_checkup_create, name='scheduled-checkup-create'),
    path('update/<int:checkup_id>/', views.scheduled_checkup_update, name='scheduled-checkup-update'),
    path('delete/<int:checkup_id>/', views.scheduled_checkup_delete, name='scheduled-checkup-delete'),
]
