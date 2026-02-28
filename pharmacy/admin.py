from django.contrib import admin
from .models import Drug, Prescription

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ['name', 'dosage_form', 'strength', 'price', 'is_active']
    list_editable = ['price', 'is_active']

admin.site.register(Prescription)
