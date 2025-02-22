from django.contrib import admin
from .models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'userrole', 'status', 'created_by')
    list_filter = ('userrole', 'status')
    search_fields = ('user__username', 'userrole', 'status')

admin.site.register(UserProfile, UserProfileAdmin)