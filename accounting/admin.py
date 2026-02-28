from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'patient', 'payment_type', 'amount', 'is_paid', 'paid_at']
    list_filter = ['payment_type', 'is_paid']
