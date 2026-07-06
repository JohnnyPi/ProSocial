from django.contrib import admin

from apps.moderation.models import CrisisFlag, ModerationReview, TransparencyLogEntry, UserRoleAssignment

admin.site.register(UserRoleAssignment)
admin.site.register(ModerationReview)
admin.site.register(TransparencyLogEntry)
admin.site.register(CrisisFlag)
