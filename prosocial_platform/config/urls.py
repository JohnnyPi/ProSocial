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
]

handler400 = "apps.common.views.error_400"
handler403 = "apps.common.views.error_403"
handler404 = "apps.common.views.error_404"
handler500 = "apps.common.views.error_500"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
