from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0002_admissions_surgery'),
    ]

    operations = [
        migrations.AddField(
            model_name='surgery',
            name='surgery_fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='surgery',
            name='patient_full_name_signed',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='surgery',
            name='patient_signed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='surgery',
            name='patient_questions',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='surgery',
            name='patient_understanding',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='surgery',
            name='patient_voluntary',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='surgery',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft — Awaiting Patient Review'),
                    ('patient_reviewed', 'Patient Reviewed — Awaiting Payment'),
                    ('paid', 'Paid — Scheduled'),
                    ('scheduled', 'Scheduled'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                ],
                default='draft',
                max_length=20,
            ),
        ),
    ]
