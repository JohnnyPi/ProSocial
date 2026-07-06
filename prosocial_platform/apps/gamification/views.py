from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.gamification.models import UserBadge, XPTransaction
from apps.gamification.services import get_or_create_gamification_profile


@login_required
def progress_dashboard(request: HttpRequest) -> HttpResponse:
    profile = get_or_create_gamification_profile(user=request.user)
    recent_xp = XPTransaction.objects.filter(user=request.user).order_by("-created_at")[:20]
    badges = UserBadge.objects.filter(user=request.user).select_related("badge")
    return render(
        request,
        "gamification/progress.html",
        {"profile": profile, "recent_xp": recent_xp, "badges": badges},
    )
