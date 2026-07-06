from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import AccountDeletionRequest, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "public_id", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email", "public_id")
    readonly_fields = ("public_id", "date_joined", "last_login")
    fieldsets = DjangoUserAdmin.fieldsets + (("Public identity", {"fields": ("public_id",)}),)


@admin.register(AccountDeletionRequest)
class AccountDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "scheduled_for", "cancelled_at", "processed_at", "created_at")
    list_filter = ("processed_at", "cancelled_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
