from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.common.models import ActivityEventType, ReactionCategory
from apps.common.services import record_activity_event
from apps.trust.anti_gaming import apply_time_decay, compute_effective_weight
from apps.trust.models import (
    DomainReputation,
    PeerRating,
    PeerRatingDimension,
    PrivilegeDefinition,
    TrustEvent,
    TrustEventType,
    UserPrivilege,
    UserTrustProfile,
)

DOMAIN_EVENT_LIMIT = 100
REACTION_BASE_WEIGHT = 2.0

CATEGORY_WEIGHTS = {
    ReactionCategory.SUPPORT: 2.0,
    ReactionCategory.CLARITY: 2.0,
    ReactionCategory.KNOWLEDGE: 2.5,
    ReactionCategory.CIVILITY: 1.5,
    ReactionCategory.CONCERN: 0.5,
}


class TrustError(Exception):
    pass


def get_or_create_trust_profile(*, user) -> UserTrustProfile:
    profile, _ = UserTrustProfile.objects.get_or_create(user=user)
    return profile


@transaction.atomic
def set_helper_style(*, user, helper_style: str) -> UserTrustProfile:
    profile = get_or_create_trust_profile(user=user)
    profile.helper_style = helper_style
    profile.helper_style_completed_at = timezone.now()
    profile.save(update_fields=["helper_style", "helper_style_completed_at", "updated_at"])
    return profile


def _emit_trust_event(
    *,
    user,
    event_type: str,
    base_weight: float,
    rater=None,
    post=None,
    reply=None,
    source_type: str = "",
    source_id: str = "",
    metadata: dict | None = None,
) -> TrustEvent:
    weight = base_weight
    if rater and settings.FUNCTIONAL_TRUST_FEATURES.get("anti_gaming"):
        weight = compute_effective_weight(
            base_weight=base_weight,
            rater=rater,
            target_user=user,
            post=post,
            reply=reply,
        )
    event = TrustEvent.objects.create(
        user=user,
        event_type=event_type,
        weight=weight,
        source_type=source_type,
        source_id=source_id,
        metadata=metadata or {},
    )
    return event


@transaction.atomic
def create_peer_rating(*, rater, post=None, reply=None, dimension: str) -> PeerRating:
    if dimension not in {d.value for d in PeerRatingDimension}:
        raise TrustError("Invalid rating dimension.")
    if rater.pk == (reply.author_id if reply else post.author_id):
        raise TrustError("You cannot rate your own content.")
    rating, created = PeerRating.objects.get_or_create(
        rater=rater,
        post=post,
        reply=reply,
        dimension=dimension,
        defaults={"is_positive": False},
    )
    if not created:
        raise TrustError("You already rated this content.")
    subject = reply.author if reply else post.author
    _emit_trust_event(
        user=subject,
        event_type=TrustEventType.PEER_RATING_NEGATIVE,
        base_weight=-1.0,
        rater=rater,
        post=post,
        reply=reply,
        source_type="reply" if reply else "post",
        source_id=str(reply.pk if reply else post.pk),
        metadata={"dimension": dimension},
    )
    record_activity_event(
        event_type=ActivityEventType.PEER_RATING_GIVEN,
        actor=rater,
        metadata={"dimension": dimension, "positive": False},
    )
    recalculate_trust_scores(user=subject)
    return rating


@transaction.atomic
def record_prosocial_reaction_trust(
    *,
    sender,
    subject,
    kind: str,
    category: str,
    post=None,
    reply=None,
) -> None:
    if not settings.FUNCTIONAL_TRUST_FEATURES.get("prosocial_reactions"):
        return
    base_weight = CATEGORY_WEIGHTS.get(category, REACTION_BASE_WEIGHT)
    _emit_trust_event(
        user=subject,
        event_type=TrustEventType.PROSOCIAL_REACTION,
        base_weight=base_weight,
        rater=sender,
        post=post,
        reply=reply,
        source_type="prosocial_reaction",
        source_id=kind,
        metadata={"kind": kind, "category": category},
    )
    recalculate_domain_reputation(user=subject, category=category)
    recalculate_trust_scores(user=subject)


def recalculate_domain_reputation(*, user, category: str) -> DomainReputation:
    events = TrustEvent.objects.filter(
        user=user,
        event_type=TrustEventType.PROSOCIAL_REACTION,
        metadata__category=category,
    ).order_by("-created_at")[:DOMAIN_EVENT_LIMIT]
    total = 0.0
    for event in events:
        total += apply_time_decay(weight=event.weight, created_at=event.created_at)
    score = min(100.0, max(0.0, total * 5.0))
    rep, _ = DomainReputation.objects.update_or_create(
        user=user,
        category=category,
        defaults={"score": round(score, 2)},
    )
    return rep


def recalculate_trust_scores(*, user) -> UserTrustProfile:
    profile = get_or_create_trust_profile(user=user)
    events = TrustEvent.objects.filter(user=user).order_by("-created_at")[:200]
    positive_weight = sum(
        apply_time_decay(weight=e.weight, created_at=e.created_at) for e in events if e.weight > 0
    )
    negative_weight = abs(
        sum(
            apply_time_decay(weight=e.weight, created_at=e.created_at)
            for e in events
            if e.weight < 0
        )
    )
    ets = min(100.0, max(0.0, 40.0 + positive_weight * 2.0 - negative_weight * 3.0))
    from apps.follows.models import UserFollow
    from apps.knowledge.models import Clip

    followers = UserFollow.objects.filter(following=user).count()
    clips_by_others = Clip.objects.filter(post__author=user).exclude(owner=user).count()
    pts = min(100.0, max(0.0, followers * 2.0 + clips_by_others * 3.0))
    contribution = (ets * 0.65) + (pts * 0.35)
    profile.engagement_trust_score = round(ets, 2)
    profile.popularity_trust_score = round(pts, 2)
    profile.contribution_score = round(contribution, 2)
    profile.behavior_score = min(100.0, max(0.0, profile.behavior_score * 0.9 + ets * 0.1))
    profile.save(
        update_fields=[
            "engagement_trust_score",
            "popularity_trust_score",
            "contribution_score",
            "behavior_score",
            "updated_at",
        ]
    )
    record_activity_event(
        event_type=ActivityEventType.TRUST_SCORE_UPDATED,
        actor=user,
        metadata={"ets": ets, "pts": pts, "contribution": contribution},
    )
    from apps.moderation.services import sync_user_role

    sync_user_role(user=user)
    if settings.FUNCTIONAL_TRUST_FEATURES.get("earned_privileges"):
        evaluate_privileges(user=user)
    return profile


def evaluate_privileges(*, user) -> list[UserPrivilege]:
    if not settings.FUNCTIONAL_TRUST_FEATURES.get("earned_privileges"):
        return []
    granted: list[UserPrivilege] = []
    profile = get_or_create_trust_profile(user=user)
    for priv_def in PrivilegeDefinition.objects.all():
        criteria = priv_def.criteria or {}
        category = criteria.get("category")
        min_score = criteria.get("min_score", 0)
        if category:
            rep = DomainReputation.objects.filter(user=user, category=category).first()
            if not rep or rep.score < min_score:
                UserPrivilege.objects.filter(user=user, privilege=priv_def, is_active=True).update(
                    is_active=False
                )
                continue
        if criteria.get("ets_min") and profile.engagement_trust_score < criteria["ets_min"]:
            UserPrivilege.objects.filter(user=user, privilege=priv_def, is_active=True).update(
                is_active=False
            )
            continue
        up, _ = UserPrivilege.objects.update_or_create(
            user=user,
            privilege=priv_def,
            domain_scope=priv_def.domain,
            defaults={"is_active": True},
        )
        granted.append(up)
    return granted


def user_has_privilege(*, user, slug: str) -> bool:
    return UserPrivilege.objects.filter(user=user, privilege__slug=slug, is_active=True).exists()


def ets_meets_threshold(*, user, threshold: float) -> bool:
    profile = get_or_create_trust_profile(user=user)
    return profile.engagement_trust_score >= threshold


def role_eligible(*, user, ets_min: float, contribution_min: float) -> bool:
    profile = get_or_create_trust_profile(user=user)
    if profile.engagement_trust_score < ets_min:
        return False
    return profile.contribution_score >= contribution_min


def seed_privilege_definitions() -> int:
    defaults = [
        {
            "slug": "can_tag_posts",
            "name": "Tag posts",
            "criteria": {"category": ReactionCategory.KNOWLEDGE, "min_score": 20},
        },
        {
            "slug": "can_submit_context_notes",
            "name": "Submit context notes",
            "criteria": {"category": ReactionCategory.CLARITY, "min_score": 30},
        },
        {
            "slug": "can_review_notes",
            "name": "Review context notes",
            "criteria": {"category": ReactionCategory.CLARITY, "min_score": 50, "ets_min": 60},
        },
        {
            "slug": "can_flag_high_priority",
            "name": "Flag high priority",
            "criteria": {"ets_min": 50},
        },
    ]
    count = 0
    for item in defaults:
        _, created = PrivilegeDefinition.objects.get_or_create(
            slug=item["slug"],
            defaults={
                "name": item["name"],
                "criteria": item["criteria"],
            },
        )
        if created:
            count += 1
    return count
