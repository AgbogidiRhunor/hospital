from django.db import models
from django.conf import settings


class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('lab', 'Lab Tests'),
        ('prescription', 'Prescription / Drugs'),
        ('admission', 'Ward Admission'),
        ('surgery', 'Surgery'),
        ('admission_medication', 'Ward Medication'),
    ]

    visit = models.ForeignKey('records.PatientVisit', on_delete=models.CASCADE, related_name='payments')
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    accountant = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='payments_processed')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    lab_request = models.ForeignKey('lab.LabRequest', null=True, blank=True, on_delete=models.SET_NULL, related_name='payment_records')
    prescription = models.ForeignKey('pharmacy.Prescription', null=True, blank=True, on_delete=models.SET_NULL, related_name='payment_records')
    created_at = models.DateTimeField(auto_now_add=True)
    admission = models.ForeignKey('records.WardAdmission', null=True, blank=True, on_delete=models.SET_NULL, related_name='payments')
    surgery = models.ForeignKey('records.Surgery', null=True, blank=True, on_delete=models.SET_NULL, related_name='payments')
    accountant_dashboard_deleted = models.BooleanField(default=False)

    # Instalment / grouping fields
    payment_group = models.CharField(max_length=100, blank=True, default='')
    part_number = models.PositiveIntegerField(default=1)
    total_parts = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment #{self.pk} — {self.get_payment_type_display()} — {self.patient.display_name}'

    @property
    def receipt_number(self):
        return f'RCP-{self.pk:05d}'
