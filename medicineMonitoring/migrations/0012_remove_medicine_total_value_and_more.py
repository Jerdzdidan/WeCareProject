# Generated by Django 5.1.4 on 2025-03-15 08:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('medicineMonitoring', '0011_alter_medicinestock_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medicine',
            name='total_value',
        ),
        migrations.RemoveField(
            model_name='medicine',
            name='unit_price',
        ),
    ]
