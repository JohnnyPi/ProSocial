from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.moderation.models import ModerationReview, ModerationReviewStatus, PlatformRole
from apps.moderation.services import review_content


def _is_moderator(user) -> bool:
    return user.role_assignments.filter(
        role__in=[PlatformRole.MODERATOR, PlatformRole.COMMUNITY_GUIDE, PlatformRole.COMMUNITY_LEADER],
        is_active=True,
    ).exists()


@login_required
@user_passes_test(_is_moderator)
def moderation_queue(request: HttpRequest) -> HttpResponse:
    reviews = ModerationReview.objects.filter(status=ModerationReviewStatus.PENDING).order_by("created_at")
    return render(request, "moderation/queue.html", {"reviews": reviews})


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
