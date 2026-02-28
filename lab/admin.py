from django.contrib import admin
from .models import LabTest, LabRequest, LabRequestTest

@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active']
    list_editable = ['price', 'is_active']

admin.site.register(LabRequest)
admin.site.register(LabRequestTest)
