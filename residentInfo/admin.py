from django.contrib import admin
from .models import Family, Resident

# Register your models here.
@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('family_no', 'date_updated')
    search_fields = ('family_no',)

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = (
        'last_name', 'first_name', 'family', 'relationship_to_head',
        'birthdate', 'age', 'civil_status', 'gender', 'category',
        'present_address', 'contact_number', 'date_updated'
    )
    list_filter = ('gender', 'category', 'civil_status', 'relationship_to_head')
    search_fields = ('last_name', 'first_name', 'family__family_no')
