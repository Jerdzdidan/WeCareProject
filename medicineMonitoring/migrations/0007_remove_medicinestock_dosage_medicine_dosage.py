# Generated by Django 5.1.4 on 2025-02-26 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicineMonitoring', '0006_medicine_total_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medicinestock',
            name='dosage',
        ),
        migrations.AddField(
            model_name='medicine',
            name='dosage',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
