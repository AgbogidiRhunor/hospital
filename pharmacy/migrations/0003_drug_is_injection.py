from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('pharmacy', '0002_prescriptiondrug_injection_fields')]
    operations = [
        migrations.AddField(model_name='drug', name='is_injection', field=models.BooleanField(default=False)),
    ]
