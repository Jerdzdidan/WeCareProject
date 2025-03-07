from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_list, name='patient-list'),

    # Patient CRUD
    path('select/', views.patient_select, name='patient-select'),
    path('create/<str:resident_id>/', views.patient_create_details, name='patient-create-details'),
    path('update/<str:pk>/', views.patient_update, name='patient-update'),
    path('delete/<str:pk>/', views.patient_delete_confirm, name='patient-delete-confirm'),

    # PATIENT AND MEDICAL RECORD CRUD
    path('detail/<str:pk>/', views.patient_detail, name='patient-detail'),

    # MEDICINE TRACKING
    path('detail/<str:pk>/medicine-tracking/select/', views.medicine_tracking_select, name='medicine-tracking-select'),
    path('detail/<str:pk>/medicine-tracking/create/<int:medicine_id>/', views.medicine_tracking_create_details, name='medicine-tracking-create-details'),
    path('medicine-tracking/delete/<int:tracking_id>/', views.medicine_tracking_delete, name='medicine-tracking-delete'),
    path('medicine-tracking/update/<int:tracking_id>/', views.medicine_tracking_update, name='medicine-tracking-update'),

    path('detail/<str:pk>/record/create/', views.medical_record_create, name='medical-record-create'),
    path('medical-record/update/<int:record_id>/', views.medical_record_update, name='medical-record-update'),
    path('<str:patient_pk>/medical-record/delete/<int:record_id>/', views.medical_record_delete, name='medical-record-delete'),

]