# Generated by Django 5.1.4 on 2025-03-20 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logs',
            name='action',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='logs',
            name='module',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='logs',
            name='performed_to',
            field=models.CharField(max_length=100),
        ),
    ]
