from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.profiles.forms import ProfileForm
from apps.profiles.selectors import get_public_profile
from apps.profiles.services import update_profile


def profile_detail(request: HttpRequest, handle: str) -> HttpResponse:
    profile = get_public_profile(handle=handle)
    from apps.profiles.models import ScopedEndorsement

    endorsements = ScopedEndorsement.objects.filter(user=profile.user, is_active=True)
    return render(
        request,
        "profiles/detail.html",
        {"profile": profile, "endorsements": endorsements},
    )


@login_required
def endorsement_create(request: HttpRequest) -> HttpResponse:
    from apps.profiles.models import VerificationMethod
    from apps.profiles.services import create_endorsement

    if request.method == "POST":
        create_endorsement(
            user=request.user,
            claim_type=request.POST.get("claim_type", ""),
            claim_label=request.POST.get("claim_label", ""),
            verification_method=request.POST.get(
                "verification_method", VerificationMethod.SELF_ASSERTED
            ),
            issuer=request.POST.get("issuer", ""),
            scope=request.POST.get("scope", ""),
        )
        return redirect("profiles:detail", handle=request.user.profile.handle)
    return render(request, "profiles/endorsement_form.html")


@login_required
def profile_edit(request: HttpRequest) -> HttpResponse:
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        form.actor = request.user
        if form.is_valid():
            update_profile(profile=profile, cleaned_data=form.cleaned_data)
            return render(
                request,
                "profiles/edit.html",
                {"form": form, "saved": True},
            )
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profiles/edit.html", {"form": form, "saved": False})
