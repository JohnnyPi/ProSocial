from django.contrib import admin

from apps.profiles.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("handle", "display_name", "user", "created_at")
    search_fields = ("handle", "display_name", "user__username")
    readonly_fields = ("created_at", "updated_at")
