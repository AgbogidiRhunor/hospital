from django.urls import path
from . import views

urlpatterns = [
    path('', views.accountant_dashboard, name='accountant_dashboard'),
    path('confirm/<int:payment_id>/', views.confirm_payment, name='confirm_payment'),
    path('delete-processed/<int:payment_id>/', views.delete_processed, name='delete_processed_payment'),
    path('receipt/<int:payment_id>/print/', views.print_receipt, name='print_receipt'),
]
