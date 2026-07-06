import uuid
from dataclasses import dataclass, field

from django.db.models import Count, Exists, OuterRef, Prefetch, Q, QuerySet
from django.shortcuts import get_object_or_404

from apps.common.models import ReactionCategory
from apps.interactions.models import (
    ContextNote,
    ContextNoteStatus,
    HiddenPost,
    Notification,
    ProsocialReaction,
    ProsocialReactionKind,
    Reply,
    UserBlock,
    UserMute,
)

REACTION_KIND_LABELS = [
    (ProsocialReactionKind.HELPFUL, "Helpful"),
    (ProsocialReactionKind.KIND, "Kind"),
    (ProsocialReactionKind.CLARIFIED, "Clarified"),
    (ProsocialReactionKind.SUPPORTIVE, "Supportive"),
    (ProsocialReactionKind.GOOD_FAITH, "Good faith"),
    (ProsocialReactionKind.NEEDS_CONTEXT, "Needs context"),
    (ProsocialReactionKind.THANKS, "Thanks"),
]


@dataclass
class ReactionItem:
    kind: str
    label: str
    count: int
    active: bool


@dataclass
class CategoryTotal:
    slug: str
    label: str
    count: int


@dataclass
class ReactionSummary:
    items: list[ReactionItem] = field(default_factory=list)
    category_totals: list[CategoryTotal] = field(default_factory=list)


def is_blocked(*, user_a, user_b) -> bool:
    """Return True if either user has blocked the other."""
    if not user_a or not user_b or user_a.pk == user_b.pk:
        return False
    return UserBlock.objects.filter(
        Q(blocking_user=user_a, blocked_user=user_b) | Q(blocking_user=user_b, blocked_user=user_a)
    ).exists()


def get_post_replies(*, post) -> QuerySet[Reply]:
    visible_children = Reply.objects.visible().select_related("author", "author__profile")
    has_visible_child = Exists(
        Reply.objects.filter(
            parent_id=OuterRef("pk"),
            deleted_at__isnull=True,
        )
    )
    return (
        Reply.objects.filter(post=post)
        .annotate(_has_visible_child=has_visible_child)
        .filter(Q(deleted_at__isnull=True) | Q(_has_visible_child=True))
        .select_related("author", "author__profile")
        .prefetch_related(Prefetch("children", queryset=visible_children))
        .order_by("created_at")
    )


def get_user_notifications(*, user, unread_only: bool = False):
    qs = Notification.objects.filter(recipient=user).select_related("actor", "post", "reply")
    if unread_only:
        qs = qs.filter(read_at__isnull=True)
    return qs


def get_unread_notification_count(*, user) -> int:
    return Notification.objects.filter(recipient=user, read_at__isnull=True).count()


def get_hidden_posts(*, user):
    return HiddenPost.objects.filter(user=user).select_related("post", "post__author__profile")


def apply_user_boundaries_to_feed(*, queryset, user):
    if not user or not user.is_authenticated:
        return queryset
    muted = UserMute.objects.filter(muting_user=user).values_list("muted_user_id", flat=True)
    excluded_users = set(muted)
    for blocker_id, blocked_id in UserBlock.objects.filter(
        Q(blocking_user=user) | Q(blocked_user=user)
    ).values_list("blocking_user_id", "blocked_user_id"):
        excluded_users.add(blocked_id if blocker_id == user.pk else blocker_id)
    hidden_post_ids = HiddenPost.objects.filter(user=user).values_list("post_id", flat=True)
    return queryset.exclude(author_id__in=excluded_users).exclude(pk__in=hidden_post_ids)


def get_reply_for_display(*, public_id: uuid.UUID) -> Reply:
    return get_object_or_404(
        Reply.objects.visible().select_related("author", "author__profile", "post"),
        public_id=public_id,
    )


def get_owned_reply(*, public_id: uuid.UUID, author) -> Reply:
    return get_object_or_404(
        Reply.objects.filter(author=author, deleted_at__isnull=True),
        public_id=public_id,
    )


def get_reaction_summary(*, post=None, reply=None, user=None) -> ReactionSummary:
    qs = ProsocialReaction.objects.all()
    if post:
        qs = qs.filter(post=post)
    elif reply:
        qs = qs.filter(reply=reply)
    else:
        return ReactionSummary()

    counts = dict(qs.values("kind").annotate(c=Count("id")).values_list("kind", "c"))
    category_totals: list[CategoryTotal] = []
    for row in qs.values("category").annotate(c=Count("id")):
        if row["category"]:
            category_totals.append(
                CategoryTotal(
                    slug=row["category"],
                    label=ReactionCategory(row["category"]).label,
                    count=row["c"],
                )
            )
    user_kinds: set[str] = set()
    if user and user.is_authenticated:
        user_kinds = set(qs.filter(sender=user).values_list("kind", flat=True))
    items = [
        ReactionItem(
            kind=k.value,
            label=label,
            count=counts.get(k.value, 0),
            active=k.value in user_kinds,
        )
        for k, label in REACTION_KIND_LABELS
    ]
    return ReactionSummary(items=items, category_totals=category_totals)


def get_visible_context_notes(*, post):
    return ContextNote.objects.filter(post=post, status=ContextNoteStatus.VISIBLE).select_related(
        "author", "author__profile"
    )
