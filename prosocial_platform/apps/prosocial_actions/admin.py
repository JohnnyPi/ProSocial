from django.contrib import admin

from apps.prosocial_actions.models import (
    ActionAcknowledgement,
    ActionInvitation,
    ActionOpportunity,
    Commitment,
    CompletionSubmission,
)


@admin.register(ActionOpportunity)
class ActionOpportunityAdmin(admin.ModelAdmin):
    list_display = ("public_id", "creator", "status", "starts_at", "created_at")
    list_filter = ("status", "verification_mode")


@admin.register(Commitment)
class CommitmentAdmin(admin.ModelAdmin):
    list_display = ("public_id", "participant", "action", "status", "is_public")
    list_filter = ("status", "is_public")


@admin.register(CompletionSubmission)
class CompletionSubmissionAdmin(admin.ModelAdmin):
    list_display = ("commitment", "review_status", "submitted_at", "reviewed_at")


@admin.register(ActionInvitation)
class ActionInvitationAdmin(admin.ModelAdmin):
    list_display = ("public_id", "action", "inviter", "invitee", "status")


@admin.register(ActionAcknowledgement)
class ActionAcknowledgementAdmin(admin.ModelAdmin):
    list_display = ("commitment", "sender", "recipient", "created_at")
