import pytest
from django.contrib.auth import get_user_model

from apps.ai_coach.models import CivilityUserAction
from apps.ai_coach.services import (
    classify_civility,
    create_civility_prompt_event,
    finalize_civility_event,
    record_civility_action,
)
from apps.common.models import ReactionCategory
from apps.interactions.models import ProsocialReaction
from apps.interactions.services import submit_report, toggle_prosocial_reaction
from apps.moderation.models import (
    AppealStatus,
    ModerationAction,
    ModerationReview,
    ModerationReviewStatus,
)
from apps.moderation.services import resolve_appeal, review_content, submit_appeal
from apps.posts.models import Post
from apps.profiles.models import ScopedEndorsement
from apps.profiles.services import create_endorsement
from apps.trust.capabilities import CapabilityError, require_capability, user_has_capability
from apps.trust.models import DomainReputation
from apps.trust.services import seed_privilege_definitions

User = get_user_model()


@pytest.mark.django_db
def test_prosocial_reaction_creates_domain_reputation(user, other_user):
    post = Post.objects.create(author=other_user, body="Helpful gardening tip")
    toggle_prosocial_reaction(sender=user, post=post, kind="HELPFUL")
    assert ProsocialReaction.objects.filter(sender=user, post=post, kind="HELPFUL").exists()
    rep = DomainReputation.objects.filter(
        user=other_user, category=ReactionCategory.KNOWLEDGE
    ).first()
    assert rep is not None
    assert rep.score > 0


@pytest.mark.django_db
def test_civility_prompt_flow(user):
    result = classify_civility(text="You are stupid and I hate this")
    assert result.message is not None
    event = create_civility_prompt_event(user=user, text="You are stupid and I hate this")
    assert event is not None
    finalize_civility_event(
        event_id=event.pk,
        final_text="You are stupid and I hate this",
    )
    event.refresh_from_db()
    assert event.is_finalized
    assert event.user_action == CivilityUserAction.POSTED_ANYWAY


@pytest.mark.django_db
def test_moderation_appeal_reversal(user, other_user):
    seed_privilege_definitions()
    post = Post.objects.create(author=user, body="Test post")
    review = ModerationReview.objects.create(post=post, status=ModerationReviewStatus.PENDING)
    review_content(
        reviewer=other_user,
        review=review,
        status=ModerationReviewStatus.REMOVED,
        explanation="Removed for test",
    )
    action = ModerationAction.objects.get(target_user=user)
    appeal = submit_appeal(appellant=user, action=action, statement="Please restore")
    resolve_appeal(appeal=appeal, reviewer=other_user, approved=True, outcome_note="Restored")
    action.refresh_from_db()
    post.refresh_from_db()
    appeal.refresh_from_db()
    assert action.is_reversed
    assert appeal.status == AppealStatus.APPROVED


@pytest.mark.django_db
def test_capability_gate(user):
    assert user_has_capability(user=user, capability="post")
    with pytest.raises(CapabilityError):
        require_capability(user=user, capability="claim_official_role")


@pytest.mark.django_db
def test_scoped_endorsement(user):
    endorsement = create_endorsement(
        user=user,
        claim_type="teacher",
        claim_label="High school teacher",
        verification_method="SELF_ASSERTED",
    )
    assert ScopedEndorsement.objects.filter(user=user, pk=endorsement.pk).exists()


@pytest.mark.django_db
def test_report_includes_civility_context(user, other_user):
    post = Post.objects.create(author=other_user, body="Discussion")
    event = create_civility_prompt_event(user=user, text="You are stupid idiot")
    record_civility_action(
        event_id=event.pk,
        user=user,
        user_action=CivilityUserAction.POSTED_ANYWAY,
        text="You are stupid idiot",
    )
    finalize_civility_event(event_id=event.pk, post=post, final_text="You are stupid idiot")
    report = submit_report(
        reporter=other_user,
        post=post,
        reason="HARASSMENT",
        details="Bad behavior",
    )
    assert "Civility prompt context" in report.details
