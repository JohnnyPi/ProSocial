import pytest
from django.contrib.auth import get_user_model

from apps.interactions.models import ReportStatus
from apps.interactions.services import create_reply, submit_report
from apps.moderation.models import (
    CrisisFlag,
    ModerationReview,
    ModerationReviewStatus,
    PlatformRole,
    UserRoleAssignment,
)
from apps.moderation.services import (
    evaluate_user_role,
    flag_crisis_content,
    review_content,
    sync_user_role,
)
from apps.posts.models import Post
from apps.posts.services import create_post

User = get_user_model()


@pytest.mark.django_db
def test_crisis_flag_detection(user):
    post = Post.objects.create(author=user, body="I want to die and need help")
    flag = flag_crisis_content(text=post.body, post=post)
    assert flag is not None
    assert CrisisFlag.objects.filter(post=post).exists()


@pytest.mark.django_db
def test_crisis_flag_on_post_create(user):
    post = create_post(author=user, body="I want to die and need help")
    assert CrisisFlag.objects.filter(post=post).exists()


@pytest.mark.django_db
def test_crisis_flag_on_reply_create(user, other_user):
    post = Post.objects.create(author=other_user, body="How are you?")
    reply = create_reply(post=post, author=user, body="Sometimes I think about suicide")
    assert CrisisFlag.objects.filter(reply=reply).exists()


@pytest.mark.django_db
def test_submit_report_creates_moderation_review(user, other_user):
    post = Post.objects.create(author=other_user, body="Bad content")
    report = submit_report(reporter=user, post=post, reason="SPAM", details="spammy")
    assert report.status == ReportStatus.IN_REVIEW
    review = ModerationReview.objects.get(content_report=report)
    assert review.status == ModerationReviewStatus.PENDING
    assert review.post_id == post.pk


@pytest.mark.django_db
def test_review_content_updates_report(user, other_user):
    post = Post.objects.create(author=other_user, body="Reported")
    report = submit_report(reporter=user, post=post, reason="SPAM")
    review = ModerationReview.objects.get(content_report=report)
    review_content(
        reviewer=user,
        review=review,
        status=ModerationReviewStatus.APPROVED,
        explanation="No violation found.",
    )
    report.refresh_from_db()
    assert report.status == ReportStatus.RESOLVED_NO_ACTION
    assert report.resolution_note == "No violation found."


@pytest.mark.django_db
def test_review_content_removed_marks_report_actioned(user, other_user):
    post = Post.objects.create(author=other_user, body="Reported")
    report = submit_report(reporter=user, post=post, reason="SPAM")
    review = ModerationReview.objects.get(content_report=report)
    review_content(
        reviewer=user,
        review=review,
        status=ModerationReviewStatus.REMOVED,
        explanation="Removed for spam.",
    )
    report.refresh_from_db()
    assert report.status == ReportStatus.RESOLVED_ACTIONED


@pytest.mark.django_db
def test_default_role_new_member(user):
    role = evaluate_user_role(user=user)
    assert role == PlatformRole.NEW_MEMBER


@pytest.mark.django_db
def test_sync_user_role(user):
    assignment = sync_user_role(user=user)
    assert UserRoleAssignment.objects.filter(user=user, is_active=True).exists()
    assert assignment.role == PlatformRole.NEW_MEMBER
