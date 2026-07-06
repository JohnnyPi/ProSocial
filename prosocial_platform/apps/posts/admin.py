from django.contrib import admin

from apps.posts.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("public_id", "author", "moderation_status", "created_at", "deleted_at")
    list_filter = ("moderation_status", "created_at")
    search_fields = ("public_id", "author__username", "body")
    readonly_fields = ("public_id", "created_at", "updated_at")
