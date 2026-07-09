from django.contrib import admin

from users.models import CustomUser


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "is_staff", "is_superuser")
    fields = ("email", "is_active", "is_staff", "is_superuser")
    readonly_fields = ("last_login",)
