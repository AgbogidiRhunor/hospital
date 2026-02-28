from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('management', '0001_initial')]
    operations = [
        migrations.AddField('user', 'genotype', models.CharField(blank=True, max_length=5)),
        migrations.AddField('user', 'current_medications', models.TextField(blank=True, default='')),
        migrations.AddField('user', 'family_history', models.TextField(blank=True, default='')),
        migrations.AddField('user', 'surgical_history', models.TextField(blank=True, default='')),
        migrations.AddField('user', 'immunizations', models.TextField(blank=True, default='')),
        migrations.AddField('user', 'disabilities', models.TextField(blank=True, default='')),
        migrations.AddField('user', 'occupation', models.CharField(blank=True, max_length=100, default='')),
        migrations.AddField('user', 'marital_status', models.CharField(blank=True, max_length=20, default='')),
        migrations.AddField('user', 'nationality', models.CharField(blank=True, max_length=60, default='')),
        migrations.AddField('user', 'religion', models.CharField(blank=True, max_length=60, default='')),
        migrations.AddField('user', 'next_of_kin_name', models.CharField(blank=True, max_length=100, default='')),
        migrations.AddField('user', 'next_of_kin_phone', models.CharField(blank=True, max_length=20, default='')),
        migrations.AddField('user', 'next_of_kin_relationship', models.CharField(blank=True, max_length=60, default='')),
        migrations.AddField('user', 'profile_photo', models.ImageField(blank=True, null=True, upload_to='profiles/')),
    ]
