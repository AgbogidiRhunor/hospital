from django.db import models
from django.conf import settings


class Drug(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    dosage_form = models.CharField(max_length=100, blank=True)
    strength = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    is_injection = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} {self.strength}'.strip()


class Prescription(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('paid', 'Paid — At Pharmacy'),
        ('dispensed', 'Dispensed'),
        ('rejected', 'Rejected'),
    ]
    visit = models.ForeignKey('records.PatientVisit', on_delete=models.CASCADE,
                               related_name='prescriptions')
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='prescriptions')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                related_name='prescriptions_written')
    pharmacist = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='prescriptions_handled')
    accountant = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='rx_payments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    doctor_note = models.TextField(blank=True)
    pharmacist_note = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_at = models.DateTimeField(null=True, blank=True)
    dispensed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pharmacist_deleted = models.BooleanField(default=False)  # soft-delete from dispensed tab

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Rx #{self.pk} — {self.patient.display_name}'


class PrescriptionDrug(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='drugs')
    drug = models.ForeignKey(Drug, on_delete=models.PROTECT, related_name='prescribed')
    dosage = models.CharField(max_length=200, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    injection_days = models.PositiveIntegerField(null=True, blank=True)
    injection_times_per_day = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.drug.name} x{self.quantity}'
