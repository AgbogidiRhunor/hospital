# Admissions and Surgery models — to be merged into models.py

from django.db import models
from django.conf import settings

WARD_CHOICES = [
    ('general_male', 'General Male Ward'),
    ('general_female', 'General Female Ward'),
    ('general_children', 'General Children Ward'),
    ('private', 'Private Ward'),
    ('semi_private', 'Semi-Private Ward'),
]

WARD_CAPACITY = {
    'general_male': 6,
    'general_female': 6,
    'general_children': 6,
    'private': 1,
    'semi_private': 2,
}

class WardAdmission(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('paid', 'Paid — Pending Admission'),
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged'),
    ]
    visit = models.ForeignKey('PatientVisit', on_delete=models.CASCADE, related_name='admissions')
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admissions')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='admitted_patients')
    nurse = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='ward_assignments')
    accountant = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='admission_payments')

    ward = models.CharField(max_length=30, choices=WARD_CHOICES)
    bed_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')

    admission_reason = models.TextField(blank=True)
    daily_ward_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_admission_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    admitted_at = models.DateTimeField(null=True, blank=True)
    discharged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Admission #{self.pk} — {self.patient.display_name} ({self.get_ward_display()})'

    @property
    def bed_label(self):
        return f'Bed {self.bed_number}'


class AdmissionPrescription(models.Model):
    """Prescription for admitted patients — can be voided and replaced."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('voided', 'Voided'),
    ]
    admission = models.ForeignKey(WardAdmission, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='admission_prescriptions')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    voided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']


class AdmissionPrescriptionItem(models.Model):
    prescription = models.ForeignKey(AdmissionPrescription, on_delete=models.CASCADE, related_name='items')
    drug_name = models.CharField(max_length=200)  # free text for flexibility
    drug = models.ForeignKey('pharmacy.Drug', null=True, blank=True, on_delete=models.SET_NULL)
    dosage = models.CharField(max_length=200, blank=True)
    frequency = models.CharField(max_length=100, blank=True)  # e.g. "twice daily"
    quantity = models.PositiveIntegerField(default=1)
    is_drip = models.BooleanField(default=False)
    is_injection = models.BooleanField(default=False)
    injection_days = models.PositiveIntegerField(null=True, blank=True)
    injection_times_per_day = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Surgery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    visit = models.ForeignKey('PatientVisit', on_delete=models.CASCADE, related_name='surgeries')
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='surgeries')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='surgeries_performed')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Surgical procedure details
    procedure_name = models.CharField(max_length=300)
    purpose_and_benefits = models.TextField(blank=True)
    known_risks = models.TextField(blank=True)
    alternative_treatments = models.TextField(blank=True)
    anesthesia_type = models.CharField(max_length=100, blank=True)
    additional_procedures_auth = models.BooleanField(default=False)
    tissue_disposal_auth = models.BooleanField(default=False)
    residents_involved = models.BooleanField(default=False)
    observers_permitted = models.BooleanField(default=False)
    photography_permitted = models.BooleanField(default=False)
    blood_transfusion_consent = models.CharField(max_length=10, choices=[('yes','Yes'),('no','No'),('na','N/A')], default='na')
    financial_disclosure = models.TextField(blank=True)
    advance_directives = models.TextField(blank=True)
    postop_instructions = models.TextField(blank=True)
    patient_acknowledged = models.BooleanField(default=False)
    witness_name = models.CharField(max_length=100, blank=True)

    # Post-surgery admission
    admit_after_surgery = models.BooleanField(default=False)
    admission = models.ForeignKey(WardAdmission, null=True, blank=True, on_delete=models.SET_NULL, related_name='from_surgery')

    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Surgery #{self.pk} — {self.procedure_name} ({self.patient.display_name})'
