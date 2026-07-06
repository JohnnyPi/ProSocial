import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.posts.models import Post

User = get_user_model()


@pytest.mark.django_db
def test_empty_post_rejected():
    user = User.objects.create_user(
        username="frank", email="f@example.com", password="test-pass-123"
    )
    post = Post(author=user, body="   ")
    with pytest.raises(ValidationError):
        post.full_clean()


@pytest.mark.django_db
def test_text_only_post_valid():
    user = User.objects.create_user(
        username="gina", email="g@example.com", password="test-pass-123"
    )
    post = Post.objects.create(author=user, body="Hello world")
    assert post.public_id is not None


@pytest.mark.django_db
def test_soft_delete_hides_from_visible_queryset():
    user = User.objects.create_user(
        username="hank", email="h@example.com", password="test-pass-123"
    )
    post = Post.objects.create(author=user, body="Temporary")
    post.soft_delete()
    assert Post.objects.visible().filter(pk=post.pk).exists() is False
