from django.contrib import admin

from apps.moderation.models import (
    Appeal,
    AppealOutcome,
    CrisisFlag,
    ModerationAction,
    ModerationReview,
    TransparencyLogEntry,
    UserRoleAssignment,
)

admin.site.register(UserRoleAssignment)
admin.site.register(ModerationReview)
admin.site.register(ModerationAction)
admin.site.register(Appeal)
admin.site.register(AppealOutcome)
admin.site.register(TransparencyLogEntry)
admin.site.register(CrisisFlag)
