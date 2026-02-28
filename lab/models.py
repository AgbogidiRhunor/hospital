from django.db import models
from django.conf import settings


class LabTest(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f'{self.name} ({self.category})'


class LabRequest(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('paid', 'Paid — Awaiting Lab'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    visit = models.ForeignKey('records.PatientVisit', on_delete=models.CASCADE,
                               related_name='lab_requests')
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='lab_requests')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
                                related_name='lab_requests_ordered')
    lab_attendant = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='lab_requests_assigned')
    accountant = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='lab_payments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    doctor_note = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    lab_attendant_deleted = models.BooleanField(default=False)  # soft-delete from completed tab

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Lab #{self.pk} — {self.patient.display_name}'

    @property
    def all_completed(self):
        return self.tests.exists() and all(t.is_completed for t in self.tests.all())


class LabRequestTest(models.Model):
    request = models.ForeignKey(LabRequest, on_delete=models.CASCADE, related_name='tests')
    test = models.ForeignKey(LabTest, on_delete=models.PROTECT, related_name='request_entries')
    doctor_note = models.CharField(max_length=300, blank=True)
    is_completed = models.BooleanField(default=False)
    result_note = models.TextField(blank=True)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.test.name} — {"Done" if self.is_completed else "Pending"}'
