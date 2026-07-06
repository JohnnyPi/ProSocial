from django.contrib import admin, messages

from apps.profiles.models import EndorsementStatus, Profile, ScopedEndorsement, VerificationMethod
from apps.profiles.services import sync_role_verified_from_endorsement


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("handle", "display_name", "user", "created_at")
    search_fields = ("handle", "display_name", "user__username")
    readonly_fields = ("created_at", "updated_at")


@admin.action(description="Mark selected endorsements as verified")
def verify_endorsements(modeladmin, request, queryset):
    updated = 0
    for endorsement in queryset:
        if endorsement.verification_method == VerificationMethod.SELF_ASSERTED:
            continue
        endorsement.status = EndorsementStatus.VERIFIED
        endorsement.is_active = True
        endorsement.save(update_fields=["status", "is_active", "updated_at"])
        sync_role_verified_from_endorsement(endorsement=endorsement)
        updated += 1
    modeladmin.message_user(request, f"Verified {updated} endorsement(s).", messages.SUCCESS)


@admin.register(ScopedEndorsement)
class ScopedEndorsementAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "claim_label",
        "verification_method",
        "status",
        "is_active",
        "expires_at",
    )
    list_filter = ("verification_method", "status", "is_active")
    actions = [verify_endorsements]
