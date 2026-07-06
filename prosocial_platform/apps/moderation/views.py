from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from apps.moderation.models import (
    Appeal,
    AppealStatus,
    ModerationAction,
    ModerationReview,
    ModerationReviewStatus,
    PlatformRole,
)
from apps.moderation.services import resolve_appeal, review_content, submit_appeal


def _is_moderator(user) -> bool:
    """Moderator queue access is role-based; the ``moderate`` capability gates finer tools."""
    return user.role_assignments.filter(
        role__in=[
            PlatformRole.MODERATOR,
            PlatformRole.COMMUNITY_GUIDE,
            PlatformRole.COMMUNITY_LEADER,
        ],
        is_active=True,
    ).exists()


@login_required
@user_passes_test(_is_moderator)
def moderation_queue(request: HttpRequest) -> HttpResponse:
    reviews = ModerationReview.objects.filter(status=ModerationReviewStatus.PENDING).order_by(
        "created_at"
    )
    pending_appeals = Appeal.objects.filter(status=AppealStatus.PENDING).select_related(
        "moderation_action", "appellant"
    )
    return render(
        request,
        "moderation/queue.html",
        {"reviews": reviews, "pending_appeals": pending_appeals},
    )


@login_required
@user_passes_test(_is_moderator)
def moderation_review(request: HttpRequest, review_id: int) -> HttpResponse:
    review = get_object_or_404(ModerationReview, pk=review_id)
    if request.method == "POST":
        review_content(
            reviewer=request.user,
            review=review,
            status=request.POST.get("status", ModerationReviewStatus.APPROVED),
            explanation=request.POST.get("explanation", ""),
        )
        return redirect("moderation:queue")
    return render(request, "moderation/review_detail.html", {"review": review})


@login_required
def appeal_create(request: HttpRequest, action_id: int) -> HttpResponse:
    action = get_object_or_404(ModerationAction, pk=action_id)
    if action.target_user_id != request.user.pk:
        return HttpResponseForbidden("Not authorized.")
    if request.method == "POST":
        try:
            submit_appeal(
                appellant=request.user,
                action=action,
                statement=request.POST.get("statement", ""),
            )
            return redirect("moderation:history")
        except ValueError as exc:
            return render(
                request,
                "moderation/appeal_form.html",
                {"action": action, "error": str(exc)},
            )
    return render(request, "moderation/appeal_form.html", {"action": action})


@login_required
@user_passes_test(_is_moderator)
def appeal_review(request: HttpRequest, appeal_id: int) -> HttpResponse:
    appeal = get_object_or_404(Appeal, pk=appeal_id)
    if request.method == "POST":
        approved = request.POST.get("decision") == "approve"
        resolve_appeal(
            appeal=appeal,
            reviewer=request.user,
            approved=approved,
            outcome_note=request.POST.get("outcome_note", ""),
        )
        return redirect("moderation:queue")
    return render(request, "moderation/appeal_review.html", {"appeal": appeal})


@login_required
def moderation_history(request: HttpRequest) -> HttpResponse:
    actions = ModerationAction.objects.filter(target_user=request.user).order_by("-created_at")
    appeals = Appeal.objects.filter(appellant=request.user).select_related("moderation_action")
    from apps.trust.models import UserPrivilege

    privileges = UserPrivilege.objects.filter(user=request.user, is_active=True).select_related(
        "privilege"
    )
    return render(
        request,
        "moderation/history.html",
        {"actions": actions, "appeals": appeals, "privileges": privileges},
    )
