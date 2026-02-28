from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('records', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('dosage_form', models.CharField(blank=True, max_length=100)),
                ('strength', models.CharField(blank=True, max_length=100)),
                ('manufacturer', models.CharField(blank=True, max_length=200)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('pending_payment','Pending Payment'),('paid','Paid — At Pharmacy'),('dispensed','Dispensed'),('rejected','Rejected')], default='pending_payment', max_length=20)),
                ('doctor_note', models.TextField(blank=True)),
                ('pharmacist_note', models.TextField(blank=True)),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('dispensed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('pharmacist_deleted', models.BooleanField(default=False)),
                ('visit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='records.patientvisit')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to=settings.AUTH_USER_MODEL)),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prescriptions_written', to=settings.AUTH_USER_MODEL)),
                ('pharmacist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prescriptions_handled', to=settings.AUTH_USER_MODEL)),
                ('accountant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rx_payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='PrescriptionDrug',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('dosage', models.CharField(blank=True, max_length=200)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price_at_time', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drugs', to='pharmacy.prescription')),
                ('drug', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='prescribed', to='pharmacy.drug')),
            ],
        ),
    ]
