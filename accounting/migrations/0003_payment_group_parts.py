from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_remove_payment_discount_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payment_group',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='payment',
            name='part_number',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='payment',
            name='total_parts',
            field=models.PositiveIntegerField(default=1),
        ),
    ]