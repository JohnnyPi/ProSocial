from django.db import transaction
from django.utils import timezone

from apps.moderation.models import (
    CrisisFlag,
    ModerationReview,
    ModerationReviewStatus,
    PlatformRole,
    ROLE_THRESHOLDS,
    TransparencyLogEntry,
    UserRoleAssignment,
)
from apps.trust.services import role_eligible


CRISIS_PHRASES = ("kill myself", "want to die", "self-harm", "suicide", "end my life")


@transaction.atomic
def flag_crisis_content(*, text: str, post=None, reply=None) -> CrisisFlag | None:
    lower = text.lower()
    matched = next((p for p in CRISIS_PHRASES if p in lower), None)
    if not matched:
        return None
    flag = CrisisFlag.objects.create(
        post=post,
        reply=reply,
        detected_phrase=matched,
        resources_shown=True,
        moderator_notified=True,
    )
    from apps.interactions.models import Notification, NotificationKind

    from django.contrib.auth import get_user_model

    User = get_user_model()
    for mod in User.objects.filter(role_assignments__role=PlatformRole.MODERATOR, role_assignments__is_active=True)[:5]:
        Notification.objects.create(
            recipient=mod,
            kind=NotificationKind.CRISIS_REVIEW,
            post=post,
            reply=reply,
            payload={"phrase": matched},
        )
    return flag


@transaction.atomic
def enqueue_moderation_review(
    *,
    content_report=None,
    post=None,
    reply=None,
) -> ModerationReview | None:
    if not post and not reply:
        return None
    existing = ModerationReview.objects.filter(
        status=ModerationReviewStatus.PENDING,
        post=post,
        reply=reply,
    ).exists()
    if existing:
        return None
    return ModerationReview.objects.create(
        content_report=content_report,
        post=post,
        reply=reply,
        status=ModerationReviewStatus.PENDING,
    )


@transaction.atomic
def review_content(*, reviewer, review: ModerationReview, status: str, explanation: str) -> ModerationReview:
    review.reviewer = reviewer
    review.status = status
    review.explanation = explanation
    review.save()
    TransparencyLogEntry.objects.create(
        action_type=f"moderation_{status.lower()}",
        summary=explanation[:500],
        anonymized_actor_id=str(reviewer.pk)[:8],
    )
    if review.content_report_id:
        from apps.interactions.models import ReportStatus

        report = review.content_report
        report.status = ReportStatus.RESOLVED_ACTIONED
        report.resolution_note = explanation[:2000]
        report.resolved_at = timezone.now()
        report.assigned_to = reviewer
        report.save(
            update_fields=["status", "resolution_note", "resolved_at", "assigned_to"]
        )
    if review.post and status == ModerationReviewStatus.REMOVED:
        from apps.posts.models import ModerationStatus

        review.post.moderation_status = ModerationStatus.REMOVED
        review.post.save(update_fields=["moderation_status"])
    if review.reply and status == ModerationReviewStatus.REMOVED:
        review.reply.soft_delete()
    return review


def evaluate_user_role(*, user) -> PlatformRole:
    best = PlatformRole.NEW_MEMBER
    for role, (ets_min, contrib_min) in ROLE_THRESHOLDS.items():
        if role_eligible(user=user, ets_min=ets_min, contribution_min=contrib_min):
            best = role
    return best


@transaction.atomic
def sync_user_role(*, user) -> UserRoleAssignment:
    role = evaluate_user_role(user=user)
    assignment = UserRoleAssignment.objects.filter(user=user, is_active=True).first()
    if assignment and assignment.role == role:
        return assignment
    if assignment:
        assignment.is_active = False
        assignment.save(update_fields=["is_active", "updated_at"])
    return UserRoleAssignment.objects.create(user=user, role=role)
