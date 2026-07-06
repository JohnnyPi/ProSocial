from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "public_id", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email", "public_id")
    readonly_fields = ("public_id", "date_joined", "last_login")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Public identity", {"fields": ("public_id",)}),
    )
