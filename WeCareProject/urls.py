"""
URL configuration for WeCareProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('residents/', include('residentInfo.urls')),
    path('patients/', include('patientInfo.urls')),
    path('medicines/', include('medicineMonitoring.urls')),
    path('scheduled-checkup/', include('scheduledcheckup.urls')),
    path('checkup-calendar/', include('checkupcalendar.urls')),
    path('users/', include('users.urls')),
    path('login/', user_views.custom_login, name='login'),
    path('logout/', user_views.custom_logout, name='logout'),
]
