from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

from apps.common.test_data.constants import (
    TEST_EMAIL_DOMAIN,
    TEST_MARKER,
    TEST_PASSWORD,
    TEST_USERNAME_PREFIX,
    format_test_body,
    format_test_reply_body,
    format_test_title,
    reply_seed_tag,
    seed_tag,
    test_email_for_username,
)
from apps.common.test_data.fixtures import (
    TEST_GUILDS,
    TEST_POSTS,
    TEST_PROFILES,
    TEST_REPLIES,
)
from apps.guilds.models import Guild
from apps.guilds.services import create_guild, join_guild
from apps.interactions.models import Reply
from apps.interactions.services import create_reply
from apps.posts.models import Post
from apps.posts.services import create_post
from apps.profiles.models import Profile
from apps.profiles.services import update_profile
from apps.prosocial_actions.services import create_action_post

User = get_user_model()


@dataclass
class SeedResult:
    users_created: int = 0
    users_updated: int = 0
    posts_created: int = 0
    posts_skipped: int = 0
    replies_created: int = 0
    replies_skipped: int = 0
    guilds_created: int = 0
    guilds_skipped: int = 0


@dataclass
class PurgeResult:
    users_deleted: int = 0
    orphan_posts_deleted: int = 0
    dry_run: bool = False


def is_test_user(user) -> bool:
    return (
        user.username.startswith(TEST_USERNAME_PREFIX)
        and user.email.endswith(f"@{TEST_EMAIL_DOMAIN}")
        and not user.is_staff
        and not user.is_superuser
    )


def get_test_users_queryset():
    return User.objects.filter(
        username__startswith=TEST_USERNAME_PREFIX,
        email__iendswith=f"@{TEST_EMAIL_DOMAIN}",
        is_staff=False,
        is_superuser=False,
    )


def orphan_test_post_queryset():
    return Post.objects.filter(Q(body__contains=TEST_MARKER) | Q(title__contains=TEST_MARKER))


def _find_post_by_seed_id(seed_id: str) -> Post | None:
    tag = seed_tag(seed_id)
    return Post.objects.filter(body__contains=tag).first()


def _find_reply_by_seed_id(seed_id: str) -> Reply | None:
    tag = reply_seed_tag(seed_id)
    return Reply.objects.filter(body__contains=tag).first()


def _find_guild_by_seed_id(seed_id: str) -> Guild | None:
    marker = f"{TEST_MARKER}:guild={seed_id}"
    return Guild.objects.filter(description__contains=marker).first()


def _seed_profile(
    fixture,
    users_by_username: dict[str, User],
    result: SeedResult,
    created_usernames: set[str],
) -> None:
    user = users_by_username[fixture.username]
    profile = user.profile
    update_profile(
        profile=profile,
        cleaned_data={
            "handle": fixture.username,
            "display_name": fixture.display_name,
            "biography": fixture.biography,
        },
    )
    if fixture.username not in created_usernames:
        result.users_updated += 1


def _seed_post(fixture, users_by_username: dict[str, User], result: SeedResult) -> None:
    if _find_post_by_seed_id(fixture.seed_id):
        result.posts_skipped += 1
        return

    author = users_by_username[fixture.author_username]
    body = format_test_body(fixture.seed_id, fixture.body)
    title = format_test_title(fixture.seed_id, fixture.title) if fixture.title else ""

    if fixture.is_action:
        action = create_action_post(
            creator=author,
            kind=fixture.kind,
            body=body,
            location_label=fixture.location_label,
            capacity=fixture.capacity,
        )
        post = action.post
    else:
        post = create_post(author=author, body=body)

    post.kind = fixture.kind
    post.thread_type = fixture.thread_type
    if title:
        post.title = title
    post.save(update_fields=["kind", "thread_type", "title", "updated_at"])
    result.posts_created += 1


def _seed_reply(
    fixture,
    users_by_username: dict[str, User],
    replies_by_seed_id: dict[str, Reply],
    result: SeedResult,
) -> None:
    if _find_reply_by_seed_id(fixture.seed_id):
        result.replies_skipped += 1
        existing = _find_reply_by_seed_id(fixture.seed_id)
        if existing:
            replies_by_seed_id[fixture.seed_id] = existing
        return

    post = _find_post_by_seed_id(fixture.post_seed_id)
    if not post:
        return

    parent = None
    if fixture.parent_reply_seed_id:
        parent = replies_by_seed_id.get(fixture.parent_reply_seed_id)
        if not parent:
            parent = _find_reply_by_seed_id(fixture.parent_reply_seed_id)

    author = users_by_username[fixture.author_username]
    body = format_test_reply_body(fixture.seed_id, fixture.body)
    reply = create_reply(post=post, author=author, body=body, parent=parent)
    replies_by_seed_id[fixture.seed_id] = reply
    result.replies_created += 1


def _seed_guild(fixture, users_by_username: dict[str, User], result: SeedResult) -> None:
    if _find_guild_by_seed_id(fixture.seed_id):
        result.guilds_skipped += 1
        return

    creator = users_by_username[fixture.creator_username]
    marker = f"{TEST_MARKER}:guild={fixture.seed_id}"
    description = f"{marker} {fixture.description}".strip()
    guild = create_guild(
        creator=creator,
        name=fixture.name,
        description=description,
    )
    for username in fixture.member_usernames:
        join_guild(user=users_by_username[username], guild=guild)
    result.guilds_created += 1


@transaction.atomic
def seed_test_data() -> SeedResult:
    result = SeedResult()
    users_by_username: dict[str, User] = {}

    created_usernames: set[str] = set()

    for fixture in TEST_PROFILES:
        user, created = User.objects.get_or_create(
            username=fixture.username,
            defaults={
                "email": test_email_for_username(fixture.username),
            },
        )
        if created:
            user.set_password(TEST_PASSWORD)
            user.save(update_fields=["password"])
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    "handle": fixture.username,
                    "display_name": fixture.display_name,
                },
            )
            result.users_created += 1
            created_usernames.add(fixture.username)
        users_by_username[fixture.username] = user

    for fixture in TEST_PROFILES:
        _seed_profile(fixture, users_by_username, result, created_usernames)

    for fixture in TEST_POSTS:
        _seed_post(fixture, users_by_username, result)

    replies_by_seed_id: dict[str, Reply] = {}
    for fixture in TEST_REPLIES:
        _seed_reply(fixture, users_by_username, replies_by_seed_id, result)

    for fixture in TEST_GUILDS:
        _seed_guild(fixture, users_by_username, result)

    from apps.interactions.services import toggle_prosocial_reaction
    from apps.trust.services import seed_privilege_definitions

    seed_privilege_definitions()
    first_post = _find_post_by_seed_id("river-welcome")
    if first_post:
        river = users_by_username.get("test_morgan")
        if river:
            try:
                toggle_prosocial_reaction(sender=river, post=first_post, kind="HELPFUL")
            except Exception:
                pass

    return result


@transaction.atomic
def purge_test_data(*, dry_run: bool = False, force: bool = False) -> PurgeResult:
    if not settings.DEBUG and not force:
        raise RuntimeError(
            "Refusing to purge test data when DEBUG=False. Pass force=True to override."
        )

    result = PurgeResult(dry_run=dry_run)
    test_users = get_test_users_queryset()
    orphan_posts = orphan_test_post_queryset().exclude(author__in=test_users)

    result.users_deleted = test_users.count()
    result.orphan_posts_deleted = orphan_posts.count()

    if dry_run:
        return result

    test_users.delete()
    orphan_posts.delete()
    return result
