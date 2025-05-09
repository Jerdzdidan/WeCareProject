# Generated by Django 5.1.4 on 2025-03-05 12:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patientInfo', '0005_medicinetracking_total_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledCheckup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checkup_date', models.DateField()),
                ('checkup_time', models.TimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_checkups', to='patientInfo.patient')),
            ],
        ),
    ]
