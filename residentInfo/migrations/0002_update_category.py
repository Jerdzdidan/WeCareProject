from django.db import migrations

def update_category(apps, schema_editor):
    Resident = apps.get_model('residentInfo', 'Resident')
    Resident.objects.filter(category='N/A').update(category='Adult')

class Migration(migrations.Migration):

    dependencies = [
        ('residentInfo', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_category),
    ]