# Generated by Django 5.1.4 on 2025-02-22 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userprofile_created_by'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='usertype',
            new_name='userrole',
        ),
    ]
