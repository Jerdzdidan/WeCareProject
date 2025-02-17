from django.urls import path
from . import views

urlpatterns = [
    path('accounts/', views.accountlist, name='account-list'),
]