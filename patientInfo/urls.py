from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_list, name='patient-list'),
    path('select/', views.patient_select, name='patient-select'),
    path('create/<str:resident_id>/', views.patient_create_details, name='patient-create-details'),
    path('update/<str:pk>/', views.patient_update, name='patient-update'),
    path('delete/<str:pk>/', views.patient_delete_confirm, name='patient-delete-confirm'),
    path('detail/<str:pk>/', views.patient_detail, name='patient-detail'),
    path('detail/<str:pk>/record/create/', views.medical_record_create, name='medical-record-create'),
    path('detail/<str:pk>/medicine/create/', views.medicine_tracking_create, name='medicine-tracking-create'),
    path('medical-record/create/<str:pk>/', views.medical_record_create, name='medical-record-create'),
    path('medical-record/update/<int:record_id>/', views.medical_record_update, name='medical-record-update'),
    path('medical-record/delete/<int:record_id>/', views.medical_record_delete, name='medical-record-delete'),
]
