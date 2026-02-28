from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_soft_delete'),
        ('records', '0003_surgery_patient_workflow'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='admission',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='records.wardadmission'),
        ),
        migrations.AddField(
            model_name='payment',
            name='surgery',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='records.surgery'),
        ),
        migrations.AddField(
            model_name='payment',
            name='surgery_payment',
            field=models.CharField(
                choices=[('consultation', 'Consultation'), ('lab', 'Lab Tests'), ('prescription', 'Prescription / Drugs'), ('admission', 'Ward Admission'), ('surgery', 'Surgery'), ('admission_medication', 'Ward Medication')],
                default='consultation',
                max_length=25,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_type',
            field=models.CharField(
                choices=[('consultation', 'Consultation'), ('lab', 'Lab Tests'), ('prescription', 'Prescription / Drugs'), ('admission', 'Ward Admission'), ('surgery', 'Surgery'), ('admission_medication', 'Ward Medication')],
                max_length=25,
            ),
        ),
    ]
