from django.contrib import admin

from apps.gamification.models import (
    Achievement,
    BadgeDefinition,
    UserBadge,
    UserGamificationProfile,
    XPTransaction,
)

admin.site.register(UserGamificationProfile)
admin.site.register(XPTransaction)
admin.site.register(BadgeDefinition)
admin.site.register(UserBadge)
admin.site.register(Achievement)
