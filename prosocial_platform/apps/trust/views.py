from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render

from apps.interactions.selectors import get_reply_for_display, is_blocked
from apps.posts.selectors import get_post_for_display
from apps.trust.forms import HelperStyleOnboardingForm, PeerRatingForm, ScoreVisibilityForm
from apps.trust.services import TrustError, create_peer_rating, get_or_create_trust_profile, set_helper_style


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


@login_required
def rate_reply(request: HttpRequest, reply_id) -> HttpResponse:
    reply = get_reply_for_display(public_id=reply_id)
    if is_blocked(user_a=request.user, user_b=reply.author):
        return HttpResponseForbidden("This interaction is not available.")
    if request.method == "POST":
        form = PeerRatingForm(request.POST)
        if form.is_valid():
            try:
                create_peer_rating(
                    rater=request.user,
                    reply=reply,
                    dimension=form.cleaned_data["dimension"],
                )
            except TrustError:
                pass
    return redirect("posts:detail", public_id=reply.post.public_id)


@login_required
def rate_post(request: HttpRequest, post_id) -> HttpResponse:
    post = get_post_for_display(public_id=post_id)
    if is_blocked(user_a=request.user, user_b=post.author):
        return HttpResponseForbidden("This interaction is not available.")
    if request.method == "POST":
        form = PeerRatingForm(request.POST)
        if form.is_valid():
            try:
                create_peer_rating(
                    rater=request.user,
                    post=post,
                    dimension=form.cleaned_data["dimension"],
                )
            except TrustError:
                pass
    return redirect("posts:detail", public_id=post.public_id)
