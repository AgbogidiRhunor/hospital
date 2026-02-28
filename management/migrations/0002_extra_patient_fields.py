from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(model_name='user', name='home_phone', field=models.CharField(blank=True, max_length=20)),
        migrations.AddField(model_name='user', name='work_phone', field=models.CharField(blank=True, max_length=20)),
        migrations.AddField(model_name='user', name='temporary_address', field=models.TextField(blank=True)),
        migrations.AddField(model_name='user', name='employer', field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name='user', name='sex_at_birth', field=models.CharField(blank=True, max_length=20)),
        migrations.AddField(model_name='user', name='has_support_person', field=models.BooleanField(default=False)),
        migrations.AddField(model_name='user', name='has_legal_guardian', field=models.BooleanField(default=False)),
    ]
