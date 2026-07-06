from django.db import transaction
from django.utils import timezone

from apps.interactions.models import (
    REACTION_KIND_TO_CATEGORY,
    ContentReport,
    ContextNote,
    ContextNoteStatus,
    HiddenPost,
    NoteRating,
    Notification,
    NotificationKind,
    ProsocialReaction,
    ProsocialReactionKind,
    Reply,
    ReportStatus,
    UserBlock,
    UserMute,
)
from apps.interactions.selectors import is_blocked
from apps.posts.models import ModerationStatus, Post


class InteractionError(Exception):
    pass


class BlockedInteractionError(InteractionError):
    pass


def _check_not_blocked(*, actor, target_user) -> None:
    if is_blocked(user_a=actor, user_b=target_user):
        raise BlockedInteractionError("This interaction is not available.")


def _create_notification(
    *,
    recipient,
    actor,
    kind: str,
    post=None,
    reply=None,
    thank_you=None,
    payload: dict | None = None,
) -> None:
    if recipient.pk == actor.pk:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        kind=kind,
        post=post,
        reply=reply,
        thank_you=thank_you,
        payload=payload or {},
    )


@transaction.atomic
def create_reply(
    *,
    post: Post,
    author,
    body: str,
    parent: Reply | None = None,
    civility_event_id: int | None = None,
    review_event_id: int | None = None,
) -> Reply:
    _check_not_blocked(actor=author, target_user=post.author)
    if parent:
        if parent.post_id != post.pk:
            raise InteractionError("Parent reply must belong to the same post.")
        if parent.parent_id is not None:
            raise InteractionError("Only one level of reply nesting is allowed.")
        _check_not_blocked(actor=author, target_user=parent.author)

    body = body.strip()
    if not body:
        raise InteractionError("Reply cannot be empty.")

    reply = Reply.objects.create(post=post, author=author, parent=parent, body=body)

    if parent:
        _create_notification(
            recipient=parent.author,
            actor=author,
            kind=NotificationKind.REPLY_TO_REPLY,
            post=post,
            reply=reply,
        )
    else:
        _create_notification(
            recipient=post.author,
            actor=author,
            kind=NotificationKind.REPLY_RECEIVED,
            post=post,
            reply=reply,
        )
    from apps.moderation.services import flag_crisis_content

    flag_crisis_content(text=reply.body, reply=reply)
    if civility_event_id:
        from apps.ai_coach.services import finalize_civility_event

        finalize_civility_event(event_id=civility_event_id, reply=reply, final_text=body)
    if review_event_id:
        from apps.ai_coach.services import finalize_content_review_event, score_from_review_event

        event = finalize_content_review_event(
            event_id=review_event_id, reply=reply, final_text=body
        )
        score_from_review_event(event=event, reply=reply)
    else:
        from apps.ai_coach.services import score_content

        score_content(text=body, reply=reply)
    return reply


@transaction.atomic
def update_reply(
    *,
    reply: Reply,
    body: str,
    civility_event_id: int | None = None,
    review_event_id: int | None = None,
) -> Reply:
    body = body.strip()
    if not body:
        raise InteractionError("Reply cannot be empty.")
    reply.body = body
    reply.save(update_fields=["body", "updated_at"])
    from apps.moderation.services import flag_crisis_content

    flag_crisis_content(text=reply.body, reply=reply)
    if civility_event_id:
        from apps.ai_coach.services import finalize_civility_event

        finalize_civility_event(event_id=civility_event_id, reply=reply, final_text=body)
    if review_event_id:
        from apps.ai_coach.services import finalize_content_review_event, score_from_review_event

        event = finalize_content_review_event(
            event_id=review_event_id, reply=reply, final_text=body
        )
        score_from_review_event(event=event, reply=reply)
    return reply


@transaction.atomic
def delete_reply(*, reply: Reply) -> Reply:
    reply.soft_delete()
    return reply


@transaction.atomic
def hide_post(*, user, post: Post) -> HiddenPost:
    hidden, _ = HiddenPost.objects.get_or_create(user=user, post=post)
    return hidden


@transaction.atomic
def unhide_post(*, user, post: Post) -> None:
    HiddenPost.objects.filter(user=user, post=post).delete()


@transaction.atomic
def mute_user(*, muting_user, muted_user) -> UserMute:
    if muting_user.pk == muted_user.pk:
        raise InteractionError("You cannot mute yourself.")
    mute, _ = UserMute.objects.get_or_create(muting_user=muting_user, muted_user=muted_user)
    return mute


@transaction.atomic
def unmute_user(*, muting_user, muted_user) -> None:
    UserMute.objects.filter(muting_user=muting_user, muted_user=muted_user).delete()


@transaction.atomic
def block_user(*, blocking_user, blocked_user, reason_code: str = "") -> UserBlock:
    if blocking_user.pk == blocked_user.pk:
        raise InteractionError("You cannot block yourself.")
    block, _ = UserBlock.objects.get_or_create(
        blocking_user=blocking_user,
        blocked_user=blocked_user,
        defaults={"optional_reason_code": reason_code},
    )
    return block


@transaction.atomic
def unblock_user(*, blocking_user, blocked_user) -> None:
    UserBlock.objects.filter(blocking_user=blocking_user, blocked_user=blocked_user).delete()


@transaction.atomic
def submit_report(
    *,
    reporter,
    post: Post | None = None,
    reply: Reply | None = None,
    reason: str,
    details: str = "",
) -> ContentReport:
    if bool(post) == bool(reply):
        raise InteractionError("Exactly one target is required.")
    if post:
        _check_not_blocked(actor=reporter, target_user=post.author)
    if reply:
        _check_not_blocked(actor=reporter, target_user=reply.author)
        if reply.post.author_id != reply.author_id:
            _check_not_blocked(actor=reporter, target_user=reply.post.author)
    report_details = details.strip()
    civility_context = _civility_context_for_target(post=post, reply=reply)
    if civility_context:
        report_details = (
            f"{report_details}\n\n[Civility prompt context: {civility_context}]".strip()
        )
    report = ContentReport.objects.create(
        reporter=reporter,
        post=post,
        reply=reply,
        reason=reason,
        details=report_details,
        status=ReportStatus.OPEN,
    )
    from apps.moderation.services import enqueue_moderation_review

    review = enqueue_moderation_review(
        content_report=report,
        post=post,
        reply=reply,
        is_high_priority=_report_is_high_priority(reporter=reporter),
    )
    if review:
        report.status = ReportStatus.IN_REVIEW
        report.save(update_fields=["status"])
    return report


@transaction.atomic
def mark_notification_read(*, notification: Notification, user) -> Notification:
    if notification.recipient_id != user.pk:
        raise InteractionError("Not authorized.")
    if notification.read_at is None:
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at"])
    return notification


@transaction.atomic
def mark_all_notifications_read(*, user) -> int:
    return Notification.objects.filter(recipient=user, read_at__isnull=True).update(
        read_at=timezone.now()
    )


def _civility_context_for_target(*, post=None, reply=None) -> str:
    from apps.ai_coach.models import CivilityPromptEvent

    qs = CivilityPromptEvent.objects.filter(is_finalized=True).order_by("-created_at")
    if post:
        event = qs.filter(post=post).first()
    elif reply:
        event = qs.filter(reply=reply).first()
    else:
        return ""
    if not event:
        return ""
    return (
        f"prompt_type={event.prompt_type}, action={event.user_action}, "
        f"edited_after_prompt={event.edited_after_prompt}"
    )


@transaction.atomic
def toggle_prosocial_reaction(
    *,
    sender,
    post: Post | None = None,
    reply: Reply | None = None,
    kind: str,
) -> tuple[bool, ProsocialReaction | None]:
    if bool(post) == bool(reply):
        raise InteractionError("Exactly one target is required.")
    target_author = post.author if post else reply.author
    if sender.pk == target_author.pk:
        raise InteractionError("You cannot react to your own content.")
    _check_not_blocked(actor=sender, target_user=target_author)
    if post and (post.deleted_at or post.moderation_status != ModerationStatus.ACTIVE):
        raise InteractionError("This content is no longer available.")
    if reply and reply.deleted_at:
        raise InteractionError("This content is no longer available.")

    category = REACTION_KIND_TO_CATEGORY.get(kind, "")
    if post:
        existing = ProsocialReaction.objects.filter(sender=sender, post=post, kind=kind).first()
        if existing:
            existing.delete()
            return False, None
        reaction = ProsocialReaction.objects.create(
            sender=sender, post=post, kind=kind, category=category
        )
    else:
        existing = ProsocialReaction.objects.filter(sender=sender, reply=reply, kind=kind).first()
        if existing:
            existing.delete()
            return False, None
        reaction = ProsocialReaction.objects.create(
            sender=sender, reply=reply, kind=kind, category=category
        )
    from apps.trust.services import record_prosocial_reaction_trust

    record_prosocial_reaction_trust(
        sender=sender,
        subject=target_author,
        kind=kind,
        category=category,
        post=post,
        reply=reply,
    )
    if kind == ProsocialReactionKind.THANKS.value:
        _create_notification(
            recipient=target_author,
            actor=sender,
            kind=NotificationKind.THANK_YOU_RECEIVED,
            post=post,
            reply=reply,
        )
    return True, reaction


def _report_is_high_priority(*, reporter) -> bool:
    from django.conf import settings

    if not settings.FUNCTIONAL_TRUST_FEATURES.get("earned_privileges"):
        return False
    from apps.trust.capabilities import user_has_capability
    from apps.trust.services import user_has_privilege

    return user_has_privilege(user=reporter, slug="can_flag_high_priority") and user_has_capability(
        user=reporter, capability="flag_high_priority"
    )


@transaction.atomic
def create_context_note(
    *, author, post: Post, body: str, sources: list | None = None
) -> ContextNote:
    from django.conf import settings

    if not settings.FUNCTIONAL_TRUST_FEATURES.get("context_notes"):
        raise InteractionError("Context notes are not enabled.")
    from apps.trust.services import user_has_privilege

    if not user_has_privilege(user=author, slug="can_submit_context_notes"):
        raise InteractionError("You have not earned the privilege to submit context notes.")
    from apps.trust.capabilities import require_capability

    require_capability(user=author, capability="submit_context_notes")
    body = body.strip()
    if not body:
        raise InteractionError("Context note cannot be empty.")
    return ContextNote.objects.create(
        author=author,
        post=post,
        body=body,
        sources=sources or [],
        status=ContextNoteStatus.PENDING,
    )


@transaction.atomic
def rate_context_note(*, rater, note: ContextNote, is_helpful: bool) -> NoteRating:
    from apps.interactions.models import RaterTrustGroup
    from apps.trust.clusters import get_user_cluster_id

    if note.status != ContextNoteStatus.VISIBLE:
        raise InteractionError("This context note is not available for rating.")
    if rater.pk == note.author_id:
        raise InteractionError("You cannot rate your own context note.")
    _check_not_blocked(actor=rater, target_user=note.author)

    rating, _ = NoteRating.objects.update_or_create(
        note=note,
        rater=rater,
        defaults={"is_helpful": is_helpful},
    )
    cluster_id = get_user_cluster_id(user=rater)
    RaterTrustGroup.objects.update_or_create(user=rater, defaults={"group_id": cluster_id})
    _evaluate_context_note_visibility(note=note)
    return rating


def _evaluate_context_note_visibility(*, note: ContextNote) -> None:
    helpful_ratings = note.ratings.filter(is_helpful=True).select_related("rater")
    group_ids = set()
    for rating in helpful_ratings:
        from apps.interactions.models import RaterTrustGroup

        group = RaterTrustGroup.objects.filter(user=rating.rater).first()
        if group:
            group_ids.add(group.group_id)
    if len(group_ids) >= 2 and helpful_ratings.count() >= 2:
        note.status = ContextNoteStatus.VISIBLE
        note.save(update_fields=["status", "updated_at"])
