from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.common.views import health_check, home_redirect

urlpatterns = [
    path("", home_redirect, name="home"),
    path("health/", health_check, name="health"),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("profiles/", include("apps.profiles.urls")),
    path("posts/", include("apps.posts.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("knowledge/", include("apps.knowledge.urls")),
    path("follows/", include("apps.follows.urls")),
    path("guilds/", include("apps.guilds.urls")),
    path("messages/", include("apps.messaging.urls")),
    path("trust/", include("apps.trust.urls")),
    path("gamification/", include("apps.gamification.urls")),
    path("ai/", include("apps.ai_coach.urls")),
    path("moderation/", include("apps.moderation.urls")),
    path("engagement/", include("apps.engagement.urls")),
    path("discovery/", include("apps.discovery.urls")),
    path("advanced/", include("apps.advanced.urls")),
    path("", include("apps.interactions.urls")),
    path("", include("apps.prosocial_actions.urls")),
]

handler400 = "apps.common.views.error_400"
handler403 = "apps.common.views.error_403"
handler404 = "apps.common.views.error_404"
handler500 = "apps.common.views.error_500"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
