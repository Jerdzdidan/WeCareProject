from django.urls import path
from . import views

urlpatterns = [
    path('', views.family_resident_list, name='resident-list'),
    
    # create, update, delete
    path('create/', views.family_resident_create, name="resident-create"),
    path('update/<int:pk>/', views.family_resident_update, name='family-update'),
    # path('delete-confirm/<int:pk>/', views.residentDeleteConfirm, name='resident-delete-confirm'),
]