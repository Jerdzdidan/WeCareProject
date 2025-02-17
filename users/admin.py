from django.contrib import admin
from .models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'usertype', 'status')
    list_filter = ('usertype', 'status')
    search_fields = ('user__username', 'usertype', 'status')

admin.site.register(UserProfile, UserProfileAdmin)