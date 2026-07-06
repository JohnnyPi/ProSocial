from __future__ import annotations

from datetime import date, datetime
from typing import Any

from django.db.models import Q
from django.utils import timezone


def _iso(value: datetime | date | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return value.isoformat()


def _user_public_id(user) -> str | None:
    if user is None:
        return None
    return str(user.public_id)


def _export_account(*, user) -> dict[str, Any]:
    return {
        "public_id": str(user.public_id),
        "username": user.username,
        "email": user.email,
        "date_joined": _iso(user.date_joined),
        "is_active": user.is_active,
    }


def _export_profile(*, user) -> dict[str, Any]:
    from apps.profiles.models import Profile

    profile = Profile.objects.filter(user=user).first()
    if profile is None:
        return {}
    return {
        "handle": profile.handle,
        "display_name": profile.display_name,
        "bio": profile.biography,
        "profile_image": profile.profile_image.name if profile.profile_image else "",
        "created_at": _iso(profile.created_at),
        "updated_at": _iso(profile.updated_at),
    }


def _export_posts(*, user) -> list[dict[str, Any]]:
    from apps.posts.models import Post

    posts = []
    for post in Post.objects.filter(author=user).order_by("created_at"):
        posts.append(
            {
                "public_id": str(post.public_id),
                "kind": post.kind,
                "thread_type": post.thread_type,
                "title": post.title,
                "body": post.body,
                "image": post.image.name if post.image else "",
                "image_alt_text": post.image_alt_text,
                "moderation_status": post.moderation_status,
                "deleted_at": _iso(post.deleted_at),
                "created_at": _iso(post.created_at),
                "updated_at": _iso(post.updated_at),
            }
        )
    return posts


def _export_replies(*, user) -> list[dict[str, Any]]:
    from apps.interactions.models import Reply

    replies = []
    for reply in Reply.objects.filter(author=user).select_related("post", "parent").order_by("created_at"):
        replies.append(
            {
                "public_id": str(reply.public_id),
                "post_public_id": str(reply.post.public_id),
                "parent_public_id": str(reply.parent.public_id) if reply.parent_id else None,
                "body": reply.body,
                "deleted_at": _iso(reply.deleted_at),
                "created_at": _iso(reply.created_at),
                "updated_at": _iso(reply.updated_at),
            }
        )
    return replies


def _export_clips(*, user) -> list[dict[str, Any]]:
    from apps.knowledge.models import Clip

    clips = []
    for clip in Clip.objects.filter(owner=user).select_related("post", "reply").order_by("created_at"):
        clips.append(
            {
                "public_id": str(clip.public_id),
                "clip_kind": clip.clip_kind,
                "quoted_text": clip.quoted_text,
                "selection_start": clip.selection_start,
                "selection_end": clip.selection_end,
                "private_note": clip.private_note,
                "post_public_id": str(clip.post.public_id) if clip.post_id else None,
                "reply_public_id": str(clip.reply.public_id) if clip.reply_id else None,
                "created_at": _iso(clip.created_at),
            }
        )
    return clips


def _export_collections(*, user) -> list[dict[str, Any]]:
    from apps.knowledge.models import Collection

    collections = []
    for collection in Collection.objects.filter(owner=user).prefetch_related("items__clip", "items__post"):
        items = []
        for item in collection.items.all():
            items.append(
                {
                    "clip_public_id": str(item.clip.public_id) if item.clip_id else None,
                    "post_public_id": str(item.post.public_id) if item.post_id else None,
                    "sort_order": item.sort_order,
                    "created_at": _iso(item.created_at),
                }
            )
        collections.append(
            {
                "public_id": str(collection.public_id),
                "title": collection.title,
                "description": collection.description,
                "visibility": collection.visibility,
                "items": items,
                "created_at": _iso(collection.created_at),
                "updated_at": _iso(collection.updated_at),
            }
        )
    return collections


def _export_journal(*, user) -> list[dict[str, Any]]:
    from apps.ai_coach.models import ReflectionJournalEntry

    return [
        {
            "prompt": entry.prompt,
            "body": entry.body,
            "ai_response": entry.ai_response,
            "trigger_event": entry.trigger_event,
            "created_at": _iso(entry.created_at),
            "updated_at": _iso(entry.updated_at),
        }
        for entry in ReflectionJournalEntry.objects.filter(user=user).order_by("created_at")
    ]


def _export_xp(*, user) -> dict[str, Any]:
    from apps.gamification.models import UserBadge, UserGamificationProfile, XPTransaction

    profile = UserGamificationProfile.objects.filter(user=user).first()
    gamification = {}
    if profile:
        gamification = {
            "total_xp": profile.total_xp,
            "level": profile.level,
            "tier": profile.tier,
            "streak_days": profile.streak_days,
            "last_activity_date": _iso(profile.last_activity_date),
            "multiplier": profile.multiplier,
        }
    transactions = [
        {
            "source": tx.source,
            "base_amount": tx.base_amount,
            "multiplier_applied": tx.multiplier_applied,
            "final_amount": tx.final_amount,
            "metadata": tx.metadata,
            "created_at": _iso(tx.created_at),
        }
        for tx in XPTransaction.objects.filter(user=user).order_by("created_at")
    ]
    badges = [
        {
            "slug": badge.badge.slug,
            "name": badge.badge.name,
            "awarded_at": _iso(badge.created_at),
        }
        for badge in UserBadge.objects.filter(user=user).select_related("badge").order_by("created_at")
    ]
    return {
        "profile": gamification,
        "transactions": transactions,
        "badges": badges,
    }


def _export_trust(*, user) -> dict[str, Any]:
    from apps.trust.models import PeerRating, TrustEvent, UserTrustProfile

    profile = UserTrustProfile.objects.filter(user=user).first()
    trust_profile = {}
    if profile:
        trust_profile = {
            "helper_style": profile.helper_style,
            "helper_style_completed_at": _iso(profile.helper_style_completed_at),
            "engagement_trust_score": profile.engagement_trust_score,
            "popularity_trust_score": profile.popularity_trust_score,
            "contribution_score": profile.contribution_score,
            "score_visibility": profile.score_visibility,
        }
    ratings_given = [
        {
            "dimension": rating.dimension,
            "is_positive": rating.is_positive,
            "post_public_id": str(rating.post.public_id) if rating.post_id else None,
            "reply_public_id": str(rating.reply.public_id) if rating.reply_id else None,
            "created_at": _iso(rating.created_at),
        }
        for rating in PeerRating.objects.filter(rater=user)
        .select_related("post", "reply")
        .order_by("created_at")
    ]
    ratings_received = [
        {
            "dimension": rating.dimension,
            "is_positive": rating.is_positive,
            "rater_public_id": _user_public_id(rating.rater),
            "post_public_id": str(rating.post.public_id) if rating.post_id else None,
            "reply_public_id": str(rating.reply.public_id) if rating.reply_id else None,
            "created_at": _iso(rating.created_at),
        }
        for rating in PeerRating.objects.filter(Q(post__author=user) | Q(reply__author=user))
        .select_related("rater", "post", "reply")
        .order_by("created_at")
    ]
    events = [
        {
            "event_type": event.event_type,
            "weight": event.weight,
            "source_type": event.source_type,
            "source_id": event.source_id,
            "metadata": event.metadata,
            "created_at": _iso(event.created_at),
        }
        for event in TrustEvent.objects.filter(user=user).order_by("created_at")
    ]
    return {
        "profile": trust_profile,
        "ratings_given": ratings_given,
        "ratings_received": ratings_received,
        "events": events,
    }


def _export_messages(*, user) -> list[dict[str, Any]]:
    from apps.messaging.models import Conversation

    conversations = []
    for conversation in Conversation.objects.filter(
        Q(participant_a=user) | Q(participant_b=user)
    ).prefetch_related("messages__sender"):
        other = conversation.other_participant(user)
        messages = [
            {
                "sender_public_id": _user_public_id(message.sender),
                "body": message.body,
                "read_at": _iso(message.read_at),
                "created_at": _iso(message.created_at),
            }
            for message in conversation.messages.order_by("created_at")
        ]
        conversations.append(
            {
                "public_id": str(conversation.public_id),
                "other_participant_public_id": _user_public_id(other),
                "messages": messages,
                "created_at": _iso(conversation.created_at),
                "updated_at": _iso(conversation.updated_at),
            }
        )
    return conversations


def _export_commitments(*, user) -> dict[str, Any]:
    from apps.prosocial_actions.models import ActionOpportunity, Commitment

    created_actions = [
        {
            "public_id": str(action.public_id),
            "post_public_id": str(action.post.public_id),
            "status": action.status,
            "location_label": action.location_label,
            "starts_at": _iso(action.starts_at),
            "ends_at": _iso(action.ends_at),
            "capacity": action.capacity,
            "verification_mode": action.verification_mode,
            "completion_instructions": action.completion_instructions,
            "created_at": _iso(action.created_at),
        }
        for action in ActionOpportunity.objects.filter(creator=user).select_related("post").order_by("created_at")
    ]
    commitments = [
        {
            "public_id": str(commitment.public_id),
            "action_public_id": str(commitment.action.public_id),
            "status": commitment.status,
            "scheduled_for": _iso(commitment.scheduled_for),
            "is_public": commitment.is_public,
            "private_note": commitment.private_note,
            "committed_at": _iso(commitment.committed_at),
            "completed_at": _iso(commitment.completed_at),
            "withdrawn_at": _iso(commitment.withdrawn_at),
            "created_at": _iso(commitment.created_at),
        }
        for commitment in Commitment.objects.filter(participant=user).select_related("action").order_by("created_at")
    ]
    return {
        "actions_created": created_actions,
        "commitments": commitments,
    }


def _export_follows(*, user) -> dict[str, Any]:
    from apps.follows.models import PostFollow, UserFollow

    return {
        "users_following": [
            {
                "public_id": _user_public_id(follow.following),
                "created_at": _iso(follow.created_at),
            }
            for follow in UserFollow.objects.filter(follower=user).select_related("following")
        ],
        "users_followed_by": [
            {
                "public_id": _user_public_id(follow.follower),
                "created_at": _iso(follow.created_at),
            }
            for follow in UserFollow.objects.filter(following=user).select_related("follower")
        ],
        "posts_followed": [
            {
                "post_public_id": str(follow.post.public_id),
                "created_at": _iso(follow.created_at),
            }
            for follow in PostFollow.objects.filter(user=user).select_related("post")
        ],
    }


def _export_boundaries(*, user) -> dict[str, Any]:
    from apps.interactions.models import HiddenPost, UserBlock, UserMute

    return {
        "muted_users": [
            {
                "public_id": _user_public_id(mute.muted_user),
                "created_at": _iso(mute.created_at),
            }
            for mute in UserMute.objects.filter(muting_user=user).select_related("muted_user")
        ],
        "blocked_users": [
            {
                "public_id": _user_public_id(block.blocked_user),
                "reason_code": block.optional_reason_code,
                "created_at": _iso(block.created_at),
            }
            for block in UserBlock.objects.filter(blocking_user=user).select_related("blocked_user")
        ],
        "hidden_posts": [
            {
                "post_public_id": str(hidden.post.public_id),
                "created_at": _iso(hidden.created_at),
            }
            for hidden in HiddenPost.objects.filter(user=user).select_related("post")
        ],
    }


def _export_notifications(*, user) -> list[dict[str, Any]]:
    from apps.interactions.models import Notification

    return [
        {
            "kind": notification.kind,
            "actor_public_id": _user_public_id(notification.actor),
            "post_public_id": str(notification.post.public_id) if notification.post_id else None,
            "reply_public_id": str(notification.reply.public_id) if notification.reply_id else None,
            "payload": notification.payload,
            "read_at": _iso(notification.read_at),
            "created_at": _iso(notification.created_at),
        }
        for notification in Notification.objects.filter(recipient=user)
        .select_related("actor", "post", "reply")
        .order_by("created_at")
    ]


def _export_donations_and_skills(*, user) -> dict[str, Any]:
    from apps.advanced.models import Donation, DonationCampaign, SkillOffering

    campaigns = [
        {
            "public_id": str(campaign.public_id),
            "title": campaign.title,
            "organization_name": campaign.organization_name,
            "description": campaign.description,
            "goal_cents": campaign.goal_cents,
            "is_verified": campaign.is_verified,
            "created_at": _iso(campaign.created_at),
        }
        for campaign in DonationCampaign.objects.filter(created_by=user).order_by("created_at")
    ]
    donations = [
        {
            "public_id": str(donation.public_id),
            "campaign_public_id": str(donation.campaign.public_id),
            "amount_cents": donation.amount_cents,
            "status": donation.status,
            "is_anonymous": donation.is_anonymous,
            "created_at": _iso(donation.created_at),
        }
        for donation in Donation.objects.filter(donor=user).select_related("campaign").order_by("created_at")
    ]
    skills = [
        {
            "public_id": str(offering.public_id),
            "skill_name": offering.skill_name,
            "description": offering.description,
            "is_remote": offering.is_remote,
            "created_at": _iso(offering.created_at),
        }
        for offering in SkillOffering.objects.filter(user=user).order_by("created_at")
    ]
    return {
        "campaigns_created": campaigns,
        "donations": donations,
        "skill_offerings": skills,
    }


def _export_guild_memberships(*, user) -> list[dict[str, Any]]:
    from apps.guilds.models import GuildMembership

    return [
        {
            "guild_public_id": str(membership.guild.public_id),
            "guild_name": membership.guild.name,
            "role": membership.role,
            "joined_at": _iso(membership.joined_at),
        }
        for membership in GuildMembership.objects.filter(user=user).select_related("guild")
    ]


def build_export_payload(*, user) -> dict[str, Any]:
    return {
        "export_version": "1.0",
        "exported_at": timezone.now().isoformat(),
        "account": _export_account(user=user),
        "profile": _export_profile(user=user),
        "posts": _export_posts(user=user),
        "replies": _export_replies(user=user),
        "clips": _export_clips(user=user),
        "collections": _export_collections(user=user),
        "journal": _export_journal(user=user),
        "xp": _export_xp(user=user),
        "trust": _export_trust(user=user),
        "messages": _export_messages(user=user),
        "commitments": _export_commitments(user=user),
        "follows": _export_follows(user=user),
        "boundaries": _export_boundaries(user=user),
        "notifications": _export_notifications(user=user),
        "donations_and_skills": _export_donations_and_skills(user=user),
        "guild_memberships": _export_guild_memberships(user=user),
    }
