import pytest
from django.test import Client

from tests.conftest import with_review_event


@pytest.mark.django_db
def test_csrf_required_on_post(user):
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    response = client.post("/dashboard/", {"body": "No CSRF"})
    assert response.status_code == 403


@pytest.mark.django_db
def test_destructive_get_not_allowed(client, user):
    from apps.posts.models import Post

    client.force_login(user)
    post = Post.objects.create(author=user, body="Test")
    response = client.get(f"/posts/{post.public_id}/delete/")
    assert response.status_code == 200
    assert Post.objects.filter(pk=post.pk, deleted_at__isnull=True).exists()


@pytest.mark.django_db
def test_post_body_escaped(client, user):
    client.force_login(user)
    page = client.get("/dashboard/")
    token = page.context["csrf_token"]
    client.post(
        "/dashboard/",
        with_review_event(
            user=user,
            data={
                "body": "<script>alert(1)</script>",
                "kind": "GENERAL",
                "thread_type": "DISCUSSION",
                "csrfmiddlewaretoken": token,
            },
        ),
    )
    response = client.get("/dashboard/")
    assert b"<script>" not in response.content
    assert b"&lt;script&gt;" in response.content
