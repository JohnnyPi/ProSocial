import pytest
from django.contrib.auth import get_user_model

from tests.conftest import with_review_event

User = get_user_model()


@pytest.mark.django_db
def test_health_endpoint(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db
def test_anonymous_home_redirects_to_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


@pytest.mark.django_db
def test_register_login_dashboard_flow(client):
    client.post(
        "/accounts/register/",
        {
            "username": "ivy",
            "email": "ivy@example.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "agree_to_terms": True,
        },
    )
    client.logout()
    login_response = client.post(
        "/accounts/login/",
        {"username": "ivy", "password": "ComplexPass123!"},
    )
    assert login_response.status_code == 302
    dashboard = client.get("/dashboard/")
    assert dashboard.status_code == 200
    assert b"Share an update" in dashboard.content


@pytest.mark.django_db
def test_create_post_appears_on_dashboard(client):
    User = get_user_model()
    user = User.objects.create_user(
        username="jane", email="j@example.com", password="test-pass-123"
    )
    client.force_login(user)
    response = client.post("/dashboard/", {"body": "My first update"}, follow=True)
    assert response.status_code == 200
    assert b"My first update" in response.content


@pytest.mark.django_db
def test_user_cannot_edit_other_users_post(client):
    User = get_user_model()
    author = User.objects.create_user(
        username="kate", email="k@example.com", password="test-pass-123"
    )
    other = User.objects.create_user(
        username="leo", email="l@example.com", password="test-pass-123"
    )
    client.force_login(author)
    client.post(
        "/dashboard/",
        with_review_event(
            user=author,
            data={"body": "Author post", "kind": "GENERAL", "thread_type": "DISCUSSION"},
        ),
    )
    post = author.posts.first()
    client.force_login(other)
    response = client.get(f"/posts/{post.public_id}/edit/")
    assert response.status_code == 404
