from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.advanced.forms import DonationCampaignForm, DonationForm, SkillOfferingForm
from apps.advanced.models import DonationCampaign, SkillOffering
from apps.advanced.services import create_donation_campaign, record_donation, request_data_export
from apps.common.rate_limit import is_rate_limited, rate_limit_key


@login_required
def donation_list(request: HttpRequest) -> HttpResponse:
    campaigns = DonationCampaign.objects.filter(is_verified=True).order_by("-created_at")
    return render(request, "advanced/donation_list.html", {"campaigns": campaigns})


@login_required
def donation_create_campaign(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = DonationCampaignForm(request.POST)
        if form.is_valid():
            campaign = create_donation_campaign(
                creator=request.user,
                title=form.cleaned_data["title"],
                organization_name=form.cleaned_data["organization_name"],
                description=form.cleaned_data.get("description", ""),
            )
            return redirect("advanced:donation_detail", public_id=campaign.public_id)
    else:
        form = DonationCampaignForm()
    return render(request, "advanced/donation_campaign_form.html", {"form": form})


@login_required
def donation_detail(request: HttpRequest, public_id) -> HttpResponse:
    campaign = DonationCampaign.objects.get(public_id=public_id)
    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            cents = int(form.cleaned_data["amount_dollars"] * 100)
            record_donation(
                donor=request.user,
                campaign=campaign,
                amount_cents=cents,
                is_anonymous=form.cleaned_data.get("is_anonymous", True),
            )
            return redirect("advanced:donation_detail", public_id=campaign.public_id)
    else:
        form = DonationForm()
    return render(request, "advanced/donation_detail.html", {"campaign": campaign, "form": form})


@login_required
def skill_list(request: HttpRequest) -> HttpResponse:
    offerings = SkillOffering.objects.select_related("user", "user__profile").order_by("-created_at")
    return render(request, "advanced/skill_list.html", {"offerings": offerings})


@login_required
def skill_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SkillOfferingForm(request.POST)
        if form.is_valid():
            offering = form.save(commit=False)
            offering.user = request.user
            offering.save()
            return redirect("advanced:skill_list")
    else:
        form = SkillOfferingForm()
    return render(request, "advanced/skill_form.html", {"form": form})


@login_required
def data_export(request: HttpRequest) -> HttpResponse:
    key = rate_limit_key("data_export", str(request.user.pk))
    if is_rate_limited(
        key=key,
        limit=settings.EXPORT_RATE_LIMIT,
        window_seconds=settings.EXPORT_RATE_WINDOW_SECONDS,
    ):
        return JsonResponse(
            {"error": "Export rate limit exceeded. Please try again later."},
            status=429,
        )
    export = request_data_export(user=request.user)
    payload = getattr(export, "_payload", {})
    response = JsonResponse(payload)
    filename = f"prosocial-export-{timezone.now().strftime('%Y%m%d')}.json"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
