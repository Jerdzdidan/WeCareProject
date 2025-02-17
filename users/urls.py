from django.urls import path
from . import views

urlpatterns = [
    path('accounts/', views.accountlist, name='account-list'),
    # create, update, delete
    # path('create/', views.accountCreate, name="account-create"),
    # path('update/', views.accountUpdate, name="account-update"),
    # path('delete/<int:pk>', views.accountDelete, name="account-delete"),
    # path('delete/<int:pk>/confirm', views.accountDeleteConfirm, name="account-delete-confirm")
]