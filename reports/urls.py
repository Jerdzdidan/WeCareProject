from django.urls import path
from . import views

urlpatterns = [
    path('residentInfo/', views.residentInfoReport, name='reports-resident-info'),
]
