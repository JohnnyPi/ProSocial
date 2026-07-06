from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.profiles.forms import ProfileForm
from apps.profiles.selectors import get_public_profile
from apps.profiles.services import update_profile


def profile_detail(request: HttpRequest, handle: str) -> HttpResponse:
    profile = get_public_profile(handle=handle)
    return render(request, "profiles/detail.html", {"profile": profile})


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
