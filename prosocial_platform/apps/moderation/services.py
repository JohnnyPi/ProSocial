from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.moderation.models import (
    ROLE_THRESHOLDS,
    Appeal,
    AppealOutcome,
    AppealStatus,
    CrisisFlag,
    ModerationAction,
    ModerationActionSource,
    ModerationActionType,
    ModerationReview,
    ModerationReviewStatus,
    PlatformRole,
    TransparencyLogEntry,
    UserRoleAssignment,
)
from apps.trust.anti_gaming import brigading_score
from apps.trust.models import TrustEvent, TrustEventType
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
    from django.contrib.auth import get_user_model

    from apps.interactions.models import Notification, NotificationKind

    User = get_user_model()
    for mod in User.objects.filter(
        role_assignments__role=PlatformRole.MODERATOR, role_assignments__is_active=True
    )[:5]:
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
    is_high_priority: bool = False,
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
        is_high_priority=is_high_priority,
    )


def _action_type_for_status(status: str) -> str:
    if status == ModerationReviewStatus.REMOVED:
        return ModerationActionType.REMOVED
    if status == ModerationReviewStatus.EDIT_REQUIRED:
        return ModerationActionType.LIMITED
    return ModerationActionType.WARNING


@transaction.atomic
def create_moderation_action(
    *,
    review: ModerationReview,
    reviewer,
    status: str,
    explanation: str,
) -> ModerationAction | None:
    if not settings.FUNCTIONAL_TRUST_FEATURES.get("moderation_actions"):
        return None
    target_user = None
    if review.post:
        target_user = review.post.author
    elif review.reply:
        target_user = review.reply.author
    if not target_user:
        return None
    source = ModerationActionSource.MODERATOR
    if review.content_report_id:
        source = ModerationActionSource.USER_REPORT
    rule_code = review.content_report.reason if review.content_report_id else "POLICY"
    action = ModerationAction.objects.create(
        target_user=target_user,
        post=review.post,
        reply=review.reply,
        moderation_review=review,
        action_type=_action_type_for_status(status),
        source=source,
        rule_code=rule_code,
        explanation=explanation,
    )
    notify_moderation_action(action=action)
    return action


@transaction.atomic
def notify_moderation_action(*, action: ModerationAction) -> None:
    from apps.interactions.models import Notification, NotificationKind

    Notification.objects.create(
        recipient=action.target_user,
        kind=NotificationKind.MODERATION_ACTION,
        post=action.post,
        reply=action.reply,
        payload={
            "action_type": action.action_type,
            "rule_code": action.rule_code,
            "source": action.source,
            "explanation": action.explanation[:500],
            "action_id": action.pk,
            "appeal_url": f"/moderation/appeal/{action.pk}/",
        },
    )


@transaction.atomic
def review_content(
    *, reviewer, review: ModerationReview, status: str, explanation: str
) -> ModerationReview:
    review.reviewer = reviewer
    review.status = status
    review.explanation = explanation
    review.save()
    TransparencyLogEntry.objects.create(
        action_type=f"moderation_{status.lower()}",
        summary=explanation[:500],
        anonymized_actor_id=str(reviewer.pk)[:8],
    )
    create_moderation_action(
        review=review,
        reviewer=reviewer,
        status=status,
        explanation=explanation,
    )
    if review.content_report_id:
        from apps.interactions.models import ReportStatus

        report = review.content_report
        if status == ModerationReviewStatus.APPROVED:
            report.status = ReportStatus.RESOLVED_NO_ACTION
        elif status == ModerationReviewStatus.REMOVED:
            report.status = ReportStatus.RESOLVED_ACTIONED
        else:
            report.status = ReportStatus.IN_REVIEW
        report.resolution_note = explanation[:2000]
        report.resolved_at = timezone.now()
        report.assigned_to = reviewer
        report.save(update_fields=["status", "resolution_note", "resolved_at", "assigned_to"])
        if report.reporter_id:
            subject = report.reporter
            if status == ModerationReviewStatus.REMOVED:
                TrustEvent.objects.create(
                    user=subject,
                    event_type=TrustEventType.MODERATION_UPHELD,
                    weight=0.5,
                    source_type="content_report",
                    source_id=str(report.pk),
                )
            elif status == ModerationReviewStatus.APPROVED:
                TrustEvent.objects.create(
                    user=subject,
                    event_type=TrustEventType.MODERATION_FRIVOLOUS,
                    weight=-0.25,
                    source_type="content_report",
                    source_id=str(report.pk),
                )
    if review.post and status == ModerationReviewStatus.REMOVED:
        from apps.posts.models import ModerationStatus

        review.post.moderation_status = ModerationStatus.REMOVED
        review.post.save(update_fields=["moderation_status"])
        if settings.FUNCTIONAL_TRUST_FEATURES.get("anti_gaming"):
            score = brigading_score(target_user=review.post.author)
            if score >= 1.0:
                enqueue_moderation_review(post=review.post)
    if review.reply and status == ModerationReviewStatus.REMOVED:
        review.reply.soft_delete()
    return review


@transaction.atomic
def submit_appeal(*, appellant, action: ModerationAction, statement: str) -> Appeal:
    if not settings.FUNCTIONAL_TRUST_FEATURES.get("moderation_appeals"):
        raise ValueError("Moderation appeals are not enabled.")
    if action.target_user_id != appellant.pk:
        raise ValueError("Only the affected user may appeal.")
    if action.is_reversed:
        raise ValueError("This action has already been reversed.")
    window = timedelta(days=settings.APPEAL_WINDOW_DAYS)
    if action.created_at < timezone.now() - window:
        raise ValueError("Appeal window has expired.")
    existing = Appeal.objects.filter(
        moderation_action=action,
        status=AppealStatus.PENDING,
    ).exists()
    if existing:
        raise ValueError("An appeal is already pending.")
    return Appeal.objects.create(
        moderation_action=action,
        appellant=appellant,
        statement=statement.strip(),
        status=AppealStatus.PENDING,
    )


@transaction.atomic
def resolve_appeal(
    *,
    appeal: Appeal,
    reviewer,
    approved: bool,
    outcome_note: str = "",
) -> Appeal:
    appeal.status = AppealStatus.APPROVED if approved else AppealStatus.DENIED
    appeal.reviewed_by = reviewer
    appeal.reviewed_at = timezone.now()
    appeal.outcome_note = outcome_note
    appeal.save()
    action = appeal.moderation_action
    reversed_action = False
    reputation_restored = False
    if approved:
        action.is_reversed = True
        action.save(update_fields=["is_reversed", "updated_at"])
        reversed_action = True
        if action.post:
            from apps.posts.models import ModerationStatus

            action.post.moderation_status = ModerationStatus.ACTIVE
            action.post.save(update_fields=["moderation_status"])
        if action.reply:
            action.reply.deleted_at = None
            action.reply.save(update_fields=["deleted_at", "updated_at"])
        TrustEvent.objects.create(
            user=action.target_user,
            event_type=TrustEventType.APPEAL_REVERSAL,
            weight=2.0,
            source_type="appeal",
            source_id=str(appeal.pk),
        )
        reputation_restored = True
        from apps.trust.services import recalculate_trust_scores

        recalculate_trust_scores(user=action.target_user)
    AppealOutcome.objects.update_or_create(
        appeal=appeal,
        defaults={
            "reversed_action": reversed_action,
            "reputation_restored": reputation_restored,
        },
    )
    return appeal


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
