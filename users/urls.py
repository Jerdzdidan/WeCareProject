from django.urls import path
from . import views

urlpatterns = [
    path('', views.accountlist, name='account-list'),
    
    # create, update, delete
    path('create/', views.accountCreate, name="account-create"),
    path('update/<int:pk>/', views.accountUpdate, name='account-update'),
    path('delete-confirm/<int:pk>/', views.accountDeleteConfirm, name='account-delete-confirm'),
]