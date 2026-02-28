from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='PatientVisit',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[
                    ('pending_payment','Pending Payment'),('paid','Paid — Awaiting Nurse'),
                    ('vitals','Nurse Taking Vitals'),('with_doctor','With Doctor'),
                    ('lab_pending','Awaiting Lab Payment'),('lab_paid','Lab Paid — Processing'),
                    ('lab_processing','Lab In Progress'),('rx_pending','Awaiting Prescription Payment'),
                    ('rx_paid','Prescription Paid — At Pharmacy'),('pharmacy','At Pharmacy'),
                    ('completed','Completed'),
                ], default='pending_payment', max_length=30)),
                ('consultation_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('chief_complaint', models.TextField(blank=True)),
                ('consultation_paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visits', to=settings.AUTH_USER_MODEL)),
                ('receptionist', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='received_visits', to=settings.AUTH_USER_MODEL)),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='doctor_visits', to=settings.AUTH_USER_MODEL)),
                ('nurse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nurse_visits', to=settings.AUTH_USER_MODEL)),
                ('accountant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accountant_visits', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='VitalSigns',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('blood_pressure', models.CharField(blank=True, max_length=20)),
                ('pulse_rate', models.CharField(blank=True, max_length=20)),
                ('temperature', models.CharField(blank=True, max_length=20)),
                ('respiratory_rate', models.CharField(blank=True, max_length=20)),
                ('oxygen_saturation', models.CharField(blank=True, max_length=20)),
                ('weight', models.CharField(blank=True, max_length=20)),
                ('height', models.CharField(blank=True, max_length=20)),
                ('bmi', models.CharField(blank=True, max_length=20)),
                ('pain_level', models.CharField(blank=True, max_length=5)),
                ('nurse_note', models.TextField(blank=True)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
                ('visit', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vitals', to='records.patientvisit')),
                ('nurse', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recorded_vitals', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorNote',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('note', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('visit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_notes', to='records.patientvisit')),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notes_written', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
