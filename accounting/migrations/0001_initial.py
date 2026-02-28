from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('records', '0001_initial'),
        ('lab', '0001_initial'),
        ('pharmacy', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('payment_type', models.CharField(choices=[('consultation','Consultation'),('lab','Lab Tests'),('prescription','Prescription / Drugs')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_paid', models.BooleanField(default=False)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('visit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='records.patientvisit')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL)),
                ('accountant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments_processed', to=settings.AUTH_USER_MODEL)),
                ('lab_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_records', to='lab.labrequest')),
                ('prescription', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_records', to='pharmacy.prescription')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
