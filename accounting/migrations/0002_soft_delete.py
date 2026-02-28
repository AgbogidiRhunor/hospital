from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('accounting', '0001_initial')]
    operations = [
        migrations.AddField('payment', 'accountant_dashboard_deleted', models.BooleanField(default=False)),
    ]
