from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.trust.forms import HelperStyleOnboardingForm, ScoreVisibilityForm
from apps.trust.services import get_or_create_trust_profile, set_helper_style


@login_required
def onboarding(request: HttpRequest) -> HttpResponse:
    profile = get_or_create_trust_profile(user=request.user)
    if profile.helper_style and request.method != "POST":
        return redirect("trust:settings")
    if request.method == "POST":
        form = HelperStyleOnboardingForm(request.POST)
        if form.is_valid():
            set_helper_style(user=request.user, helper_style=form.cleaned_data["helper_style"])
            return redirect("dashboard:knowledge")
    else:
        form = HelperStyleOnboardingForm()
    return render(request, "trust/onboarding.html", {"form": form})


@login_required
def trust_settings(request: HttpRequest) -> HttpResponse:
    profile = get_or_create_trust_profile(user=request.user)
    if request.method == "POST":
        form = ScoreVisibilityForm(request.POST)
        if form.is_valid():
            profile.score_visibility = form.cleaned_data["score_visibility"]
            profile.save(update_fields=["score_visibility", "updated_at"])
            return redirect("trust:settings")
    else:
        form = ScoreVisibilityForm(initial={"score_visibility": profile.score_visibility})
    return render(request, "trust/settings.html", {"profile": profile, "form": form})
