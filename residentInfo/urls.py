from django.urls import path
from . import views

urlpatterns = [
    path('', views.family_resident_list, name='resident-list'),
    
    # create, update, delete
    path('create/', views.family_resident_create, name="resident-create"),
    path('familyupdate/<str:pk>/', views.family_resident_update, name='family-update'),
    path('familydelete/<str:pk>/', views.family_delete_confirm, name='family-delete-confirm'),
    path('residentupdate/<str:pk>/', views.resident_update, name='resident-update'),
    path('residentdelete/<str:pk>/', views.resident_delete_confirm, name='resident-delete-confirm'),
    # path('delete-confirm/<int:pk>/', views.residentDeleteConfirm, name='resident-delete-confirm'),
]