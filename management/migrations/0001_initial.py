from django.db import migrations, models
import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]
    operations = [
        migrations.CreateModel(
            name='ConsultingRoom',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('number', models.PositiveIntegerField(unique=True)),
                ('name', models.CharField(blank=True, max_length=50)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['number']},
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()])),
                ('first_name', models.CharField(blank=True, max_length=150)),
                ('last_name', models.CharField(blank=True, max_length=150)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('role', models.CharField(choices=[('patient','Patient'),('doctor','Doctor'),('pharmacist','Pharmacist'),('lab_attendant','Lab Attendant'),('nurse','Nurse'),('receptionist','Receptionist'),('accountant','Accountant')], default='patient', max_length=20)),
                ('is_approved', models.BooleanField(default=False)),
                ('doctor_type', models.CharField(blank=True, max_length=20)),
                ('specialization', models.CharField(blank=True, max_length=50)),
                ('license_number', models.CharField(blank=True, max_length=50)),
                ('consulting_room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='occupying_doctors', to='management.consultingroom')),
                ('is_available', models.BooleanField(default=False)),
                ('is_on_sit', models.BooleanField(default=False)),
                ('is_vital_signs_nurse', models.BooleanField(default=False)),
                ('preferred_name', models.CharField(blank=True, max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, max_length=20)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('address', models.TextField(blank=True)),
                ('blood_group', models.CharField(blank=True, max_length=5)),
                ('allergies', models.TextField(blank=True)),
                ('medical_history', models.TextField(blank=True)),
                ('emergency_contact_name', models.CharField(blank=True, max_length=100)),
                ('emergency_contact_phone', models.CharField(blank=True, max_length=20)),
                ('emergency_contact_relationship', models.CharField(blank=True, max_length=60)),
                ('groups', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
            managers=[('objects', django.contrib.auth.models.UserManager())],
        ),
    ]
