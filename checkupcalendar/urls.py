from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='checkup-calendar'),
]
