from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescriptiondrug',
            name='injection_days',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='prescriptiondrug',
            name='injection_times_per_day',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
