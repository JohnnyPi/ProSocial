from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.engagement.models import Challenge
from apps.engagement.services import (
    complete_challenge,
    end_rest_mode,
    is_in_rest_mode,
    start_rest_mode,
)


@login_required
def challenge_list(request: HttpRequest) -> HttpResponse:
    challenges = Challenge.objects.filter(is_active=True).order_by("period", "title")
    return render(request, "engagement/challenge_list.html", {"challenges": challenges})


@login_required
def complete_challenge_view(request: HttpRequest, challenge_id: int) -> HttpResponse:
    challenge = Challenge.objects.get(pk=challenge_id)
    complete_challenge(user=request.user, challenge=challenge)
    return redirect("engagement:challenges")


@login_required
def rest_mode_toggle(request: HttpRequest) -> HttpResponse:
    if is_in_rest_mode(user=request.user):
        end_rest_mode(user=request.user)
    else:
        start_rest_mode(user=request.user)
    return redirect("engagement:challenges")
