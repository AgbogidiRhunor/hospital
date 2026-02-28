from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('records', '0001_initial')]
    operations = [
        migrations.AddField('patientvisit', 'visit_summary', models.TextField(blank=True, default='')),
        migrations.AddField('patientvisit', 'queue_number', models.PositiveIntegerField(null=True, blank=True)),
        migrations.AddField('patientvisit', 'nurse_history_deleted', models.BooleanField(default=False)),
    ]
