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
            name='LabTest',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['category', 'name']},
        ),
        migrations.CreateModel(
            name='LabRequest',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('pending_payment','Pending Payment'),('paid','Paid — Awaiting Lab'),('in_progress','In Progress'),('completed','Completed')], default='pending_payment', max_length=20)),
                ('doctor_note', models.TextField(blank=True)),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('lab_attendant_deleted', models.BooleanField(default=False)),
                ('visit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lab_requests', to='records.patientvisit')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lab_requests', to=settings.AUTH_USER_MODEL)),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lab_requests_ordered', to=settings.AUTH_USER_MODEL)),
                ('lab_attendant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lab_requests_assigned', to=settings.AUTH_USER_MODEL)),
                ('accountant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lab_payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='LabRequestTest',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('doctor_note', models.CharField(blank=True, max_length=300)),
                ('is_completed', models.BooleanField(default=False)),
                ('result_note', models.TextField(blank=True)),
                ('price_at_time', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='lab.labrequest')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='request_entries', to='lab.labtest')),
            ],
        ),
    ]
