from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0001_initial'),
        ('pharmacy', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WardAdmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ward', models.CharField(choices=[('general_male', 'General Male Ward'), ('general_female', 'General Female Ward'), ('general_children', 'General Children Ward'), ('private', 'Private Ward'), ('semi_private', 'Semi-Private Ward')], max_length=30)),
                ('bed_number', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('pending_payment', 'Pending Payment'), ('paid', 'Paid — Pending Admission'), ('admitted', 'Admitted'), ('discharged', 'Discharged')], default='pending_payment', max_length=20)),
                ('admission_reason', models.TextField(blank=True)),
                ('daily_ward_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_admission_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('admitted_at', models.DateTimeField(blank=True, null=True)),
                ('discharged_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('visit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admissions', to='records.patientvisit')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admissions', to=settings.AUTH_USER_MODEL)),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admitted_patients', to=settings.AUTH_USER_MODEL)),
                ('nurse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ward_assignments', to=settings.AUTH_USER_MODEL)),
                ('accountant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admission_payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='AdmissionPrescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', 'Active'), ('voided', 'Voided')], default='active', max_length=10)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('voided_at', models.DateTimeField(blank=True, null=True)),
                ('admission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='records.wardadmission')),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admission_prescriptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='AdmissionPrescriptionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drug_name', models.CharField(max_length=200)),
                ('dosage', models.CharField(blank=True, max_length=200)),
                ('frequency', models.CharField(blank=True, max_length=100)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('is_drip', models.BooleanField(default=False)),
                ('is_injection', models.BooleanField(default=False)),
                ('injection_days', models.PositiveIntegerField(blank=True, null=True)),
                ('injection_times_per_day', models.PositiveIntegerField(blank=True, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='records.admissionprescription')),
                ('drug', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pharmacy.drug')),
            ],
        ),
        migrations.CreateModel(
            name='Surgery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('procedure_name', models.CharField(max_length=300)),
                ('purpose_and_benefits', models.TextField(blank=True)),
                ('known_risks', models.TextField(blank=True)),
                ('alternative_treatments', models.TextField(blank=True)),
                ('anesthesia_type', models.CharField(blank=True, max_length=100)),
                ('additional_procedures_auth', models.BooleanField(default=False)),
                ('tissue_disposal_auth', models.BooleanField(default=False)),
                ('residents_involved', models.BooleanField(default=False)),
                ('observers_permitted', models.BooleanField(default=False)),
                ('photography_permitted', models.BooleanField(default=False)),
                ('blood_transfusion_consent', models.CharField(choices=[('yes', 'Yes'), ('no', 'No'), ('na', 'N/A')], default='na', max_length=10)),
                ('financial_disclosure', models.TextField(blank=True)),
                ('advance_directives', models.TextField(blank=True)),
                ('postop_instructions', models.TextField(blank=True)),
                ('patient_acknowledged', models.BooleanField(default=False)),
                ('witness_name', models.CharField(blank=True, max_length=100)),
                ('admit_after_surgery', models.BooleanField(default=False)),
                ('scheduled_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('visit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surgeries', to='records.patientvisit')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surgeries', to=settings.AUTH_USER_MODEL)),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='surgeries_performed', to=settings.AUTH_USER_MODEL)),
                ('admission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='from_surgery', to='records.wardadmission')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
