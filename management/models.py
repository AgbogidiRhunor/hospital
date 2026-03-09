from django.contrib.auth.models import AbstractUser
from django.db import models

SPECIALIZATIONS = [
    ('cardiology', 'Cardiology'),
    ('dermatology', 'Dermatology'),
    ('endocrinology', 'Endocrinology'),
    ('gastroenterology', 'Gastroenterology'),
    ('hematology', 'Hematology'),
    ('nephrology', 'Nephrology'),
    ('neurology', 'Neurology'),
    ('oncology', 'Oncology'),
    ('ophthalmology', 'Ophthalmology'),
    ('orthopedics', 'Orthopedics'),
    ('otolaryngology', 'ENT (Otolaryngology)'),
    ('pediatrics', 'Pediatrics'),
    ('psychiatry', 'Psychiatry'),
    ('pulmonology', 'Pulmonology'),
    ('rheumatology', 'Rheumatology'),
    ('urology', 'Urology'),
    ('radiology', 'Radiology'),
    ('surgery', 'General Surgery'),
    ('emergency', 'Emergency Medicine'),
    ('anesthesiology', 'Anesthesiology'),
    ('obstetrics', 'Obstetrics & Gynaecology'),
    ('neonatology', 'Neonatology'),
    ('pathology', 'Pathology'),
    ('infectious_disease', 'Infectious Disease'),
]

ROLES = [
    ('patient', 'Patient'),
    ('doctor', 'Doctor'),
    ('pharmacist', 'Pharmacist'),
    ('lab_attendant', 'Lab Attendant'),
    ('nurse', 'Nurse'),
    ('receptionist', 'Receptionist'),
    ('accountant', 'Accountant'),
]

DOCTOR_TYPES = [
    ('general', 'General Doctor'),
    ('specialist', 'Specialist'),
]

GENDER_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
    ("O", "Other"),
]

BLOOD_GROUPS = [('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),('O+','O+'),('O-','O-'),('AB+','AB+'),('AB-','AB-')]
GENOTYPES = [('AA','AA'),('AS','AS'),('SS','SS'),('AC','AC'),('SC','SC')]


class ConsultingRoom(models.Model):
    number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return self.name or f'Room {self.number}'

    @property
    def display_name(self):
        return self.name or f'Consulting Room {self.number}'

    @property
    def current_doctor(self):
        return self.occupying_doctors.filter(is_available=True).first()


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLES, default='patient')
    is_approved = models.BooleanField(default=False)

    # Doctor-specific
    doctor_type = models.CharField(max_length=20, choices=DOCTOR_TYPES, blank=True)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATIONS, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    consulting_room = models.ForeignKey(
        ConsultingRoom, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='occupying_doctors'
    )

    # Availability flags
    is_available = models.BooleanField(default=False)
    is_on_sit = models.BooleanField(default=False)
    is_vital_signs_nurse = models.BooleanField(default=False)

    # Basic info (all roles)
    preferred_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # Patient-specific medical
    blood_group = models.CharField(max_length=10, blank=True, choices=BLOOD_GROUPS)
    genotype = models.CharField(max_length=10, blank=True, choices=GENOTYPES)
    allergies = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    family_history = models.TextField(blank=True)
    surgical_history = models.TextField(blank=True)
    immunizations = models.TextField(blank=True)
    disabilities = models.TextField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    marital_status = models.CharField(max_length=20, blank=True,
    choices=[('single','Single'),('married','Married'),('divorced','Divorced'),('widowed','Widowed')])
    nationality = models.CharField(max_length=60, blank=True)
    religion = models.CharField(max_length=60, blank=True)
    next_of_kin_name = models.CharField(max_length=100, blank=True)
    next_of_kin_phone = models.CharField(max_length=20, blank=True)
    next_of_kin_relationship = models.CharField(max_length=60, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=60, blank=True)
    home_phone = models.CharField(max_length=20, blank=True)
    work_phone = models.CharField(max_length=20, blank=True)
    temporary_address = models.TextField(blank=True)
    employer = models.CharField(max_length=200, blank=True)
    sex_at_birth = models.CharField(max_length=20, blank=True)
    has_support_person = models.BooleanField(default=False)
    has_legal_guardian = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)

    class Meta:
        verbose_name = 'user'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.role})'

    @property
    def display_name(self):
        return self.preferred_name or self.get_full_name() or self.username

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        from datetime import date
        today = date.today()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @property
    def is_doctor(self): return self.role == 'doctor'
    @property
    def is_nurse(self): return self.role == 'nurse'
    @property
    def is_pharmacist(self): return self.role == 'pharmacist'
    @property
    def is_lab_attendant(self): return self.role == 'lab_attendant'
    @property
    def is_receptionist(self): return self.role == 'receptionist'
    @property
    def is_accountant(self): return self.role == 'accountant'
    @property
    def is_patient(self): return self.role == 'patient'


