# Generated by Django 5.1.4 on 2025-03-02 11:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patientInfo', '0003_remove_medicinetracking_medicine_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='medicinetracking',
            old_name='dosage',
            new_name='total_dosage',
        ),
    ]
