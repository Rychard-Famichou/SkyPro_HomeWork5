from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_active', 'is_staff', 'is_superuser')
    filter_horizontal = []
    list_filter = []  

admin.site.register(CustomUser,CustomUserAdmin)
