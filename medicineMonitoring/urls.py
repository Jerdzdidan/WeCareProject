from django.urls import path
from . import views

urlpatterns = [
    path('', views.medicine_list, name='medicine-list'),
    path('add/', views.medicine_add, name='medicine-add'),
    path('update/<int:pk>/', views.medicine_update, name='medicine-update'),
    path('delete/<int:pk>/', views.medicine_delete, name='medicine-delete'),
    path('<int:pk>/', views.medicine_detail, name='medicine-detail'),
    path('stock/add/<int:medicine_pk>/', views.medicine_stock_add, name='stock-add'),
    path('stock/update/<int:stock_pk>/', views.medicine_stock_update, name='stock-update'),
    path('stock/delete/<int:stock_pk>/', views.medicine_stock_delete, name='stock-delete'),
    path('stock/delete-all-expired/<int:medicine_pk>/', views.medicine_stock_delete_all_expired, name='stock-delete-all-expired'),
]
