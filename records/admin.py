from django.contrib import admin
from .models import PatientVisit, VitalSigns, DoctorNote

admin.site.register(PatientVisit)
admin.site.register(VitalSigns)
admin.site.register(DoctorNote)
