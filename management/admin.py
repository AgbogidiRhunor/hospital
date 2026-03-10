from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ConsultingRoom


@admin.register(ConsultingRoom)
class ConsultingRoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'is_active', 'current_doctor']
    list_editable = ['name', 'is_active']
    ordering = ['number']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'role', 'is_approved', 'is_available']
    list_filter = ['role', 'is_approved', 'is_available']
    list_editable = ['is_approved']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Profile', {'fields': ('role', 'is_approved', 'doctor_type', 'specialization',
                                        'license_number', 'consulting_room', 'is_available',
                                        'is_on_sit', 'is_vital_signs_nurse')}),
        ('Patient Info', {'fields': ('preferred_name', 'date_of_birth', 'gender', 'phone',
                                      'address', 'blood_group', 'allergies', 'medical_history',
                                      'emergency_contact_name', 'emergency_contact_phone',
                                      'emergency_contact_relationship')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role', 'first_name', 'last_name', 'email')}),
    )


def create_superuser(self, username, email=None, password=None, **extra_fields):
    extra_fields.setdefault("is_staff", True)
    extra_fields.setdefault("is_superuser", True)
    extra_fields.setdefault("is_active", True)
    extra_fields.setdefault("is_approved", True)
    extra_fields.setdefault("role", "doctor")

    if extra_fields.get("is_staff") is not True:
        raise ValueError("Superuser must have is_staff=True.")
    if extra_fields.get("is_superuser") is not True:
        raise ValueError("Superuser must have is_superuser=True.")

    return self.create_user(username=username, email=email, password=password, **extra_fields)