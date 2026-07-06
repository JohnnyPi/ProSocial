from django.contrib import admin

from apps.engagement.models import (
    Challenge,
    GuildMission,
    ReEngagementMessage,
    RestModeSession,
    UserChallengeProgress,
)

admin.site.register(Challenge)
admin.site.register(UserChallengeProgress)
admin.site.register(GuildMission)
admin.site.register(RestModeSession)
admin.site.register(ReEngagementMessage)
