from django.contrib import admin
from .models import Family, Resident

class ResidentInline(admin.TabularInline):
    model = Resident
    extra = 0
    can_delete = False
    fields = (
        'last_name', 'first_name', 'relationship_to_head',
        'birthdate', 'age', 'civil_status', 'gender', 'category',
        'present_address', 'contact_number', 'date_updated'
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj):
        return False

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('family_no', 'date_updated', 'list_family_members')
    inlines = [ResidentInline]

    def list_family_members(self, obj):
        # This method joins the string representations of each resident.
        return ", ".join(str(resident) for resident in obj.residents.all())
    list_family_members.short_description = 'Family Members'

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = (
        'last_name', 'first_name', 'family', 'relationship_to_head',
        'birthdate', 'age', 'civil_status', 'gender', 'category',
        'present_address', 'contact_number', 'date_updated'
    )
    list_filter = ('gender', 'category', 'civil_status', 'relationship_to_head')
    search_fields = ('last_name', 'first_name', 'family__family_no')
