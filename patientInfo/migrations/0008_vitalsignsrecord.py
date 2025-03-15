# Generated by Django 5.1.4 on 2025-03-15 13:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patientInfo', '0007_pastmedicalhistory_others'),
    ]

    operations = [
        migrations.CreateModel(
            name='VitalSignsRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blood_pressure', models.CharField(blank=True, max_length=10, null=True)),
                ('pulse_rate', models.IntegerField(blank=True, null=True)),
                ('temperature', models.FloatField(blank=True, null=True)),
                ('height', models.FloatField(blank=True, null=True)),
                ('weight', models.FloatField(blank=True, null=True)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vital_signs_records', to='patientInfo.patient')),
            ],
        ),
    ]
