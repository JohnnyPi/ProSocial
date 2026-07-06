from django.contrib import admin

from apps.interactions.models import (
    ContentReport,
    HiddenPost,
    Notification,
    Reply,
    ThankYou,
    UserBlock,
    UserMute,
)


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ("public_id", "author", "post", "created_at", "deleted_at")
    search_fields = ("public_id", "body", "author__username")
    readonly_fields = ("public_id", "created_at", "updated_at")


@admin.register(ThankYou)
class ThankYouAdmin(admin.ModelAdmin):
    list_display = ("sender", "post", "reply", "created_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "kind", "actor", "read_at", "created_at")
    list_filter = ("kind", "read_at")


@admin.register(HiddenPost)
class HiddenPostAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")


@admin.register(UserMute)
class UserMuteAdmin(admin.ModelAdmin):
    list_display = ("muting_user", "muted_user", "created_at")


@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ("blocking_user", "blocked_user", "created_at")


@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "reason", "status", "created_at", "resolved_at")
    list_filter = ("status", "reason")
    search_fields = ("details", "reporter__username")
