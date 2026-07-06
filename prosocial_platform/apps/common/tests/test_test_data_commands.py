import pytest
from django.contrib.auth import get_user_model

from apps.common.test_data.constants import TEST_MARKER, seed_tag
from apps.common.test_data.fixtures import TEST_POSTS, TEST_PROFILES
from apps.common.test_data.services import get_test_users_queryset, purge_test_data, seed_test_data
from apps.posts.models import Post
from apps.profiles.models import Profile
from apps.prosocial_actions.models import ActionOpportunity

User = get_user_model()


@pytest.mark.django_db
def test_seed_test_data_creates_profiles_and_posts():
    result = seed_test_data()

    assert result.users_created == len(TEST_PROFILES)
    assert result.posts_created == len(TEST_POSTS)
    assert get_test_users_queryset().count() == len(TEST_PROFILES)
    assert Profile.objects.filter(handle__startswith="test_").count() == len(TEST_PROFILES)

    for fixture in TEST_POSTS:
        assert Post.objects.filter(body__contains=seed_tag(fixture.seed_id)).exists()

    action_posts = [fixture for fixture in TEST_POSTS if fixture.is_action]
    assert ActionOpportunity.objects.count() == len(action_posts)


@pytest.mark.django_db
def test_seed_test_data_is_idempotent():
    first = seed_test_data()
    second = seed_test_data()

    assert first.posts_created == len(TEST_POSTS)
    assert second.posts_created == 0
    assert second.posts_skipped == len(TEST_POSTS)
    assert Post.objects.filter(body__contains=TEST_MARKER).count() == len(TEST_POSTS)


@pytest.mark.django_db
def test_purge_test_data_removes_seeded_records(user):
    seed_test_data()

    result = purge_test_data(force=True)

    assert result.users_deleted == len(TEST_PROFILES)
    assert get_test_users_queryset().count() == 0
    assert Post.objects.filter(body__contains=TEST_MARKER).count() == 0
    assert User.objects.filter(pk=user.pk).exists()


@pytest.mark.django_db
def test_purge_test_data_dry_run_does_not_delete(user):
    seed_test_data()

    result = purge_test_data(dry_run=True, force=True)

    assert result.users_deleted == len(TEST_PROFILES)
    assert get_test_users_queryset().count() == len(TEST_PROFILES)
    assert User.objects.filter(pk=user.pk).exists()
