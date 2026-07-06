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
    format_test_title,
    seed_tag,
    test_email_for_username,
)
from apps.common.test_data.fixtures import TEST_POSTS, TEST_PROFILES
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
    return Post.objects.filter(
        Q(body__contains=TEST_MARKER) | Q(title__contains=TEST_MARKER)
    )


def _find_post_by_seed_id(seed_id: str) -> Post | None:
    tag = seed_tag(seed_id)
    return Post.objects.filter(body__contains=tag).first()


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
