from dataclasses import dataclass

from apps.posts.models import PostKind, ThreadType


@dataclass(frozen=True)
class TestReplyFixture:
    seed_id: str
    post_seed_id: str
    author_username: str
    body: str
    parent_reply_seed_id: str = ""


@dataclass(frozen=True)
class TestGuildFixture:
    seed_id: str
    creator_username: str
    name: str
    description: str = ""
    member_usernames: tuple[str, ...] = ()


@dataclass(frozen=True)
class TestProfileFixture:
    username: str
    display_name: str
    biography: str


@dataclass(frozen=True)
class TestPostFixture:
    seed_id: str
    author_username: str
    body: str
    kind: str = PostKind.GENERAL
    thread_type: str = ThreadType.DISCUSSION
    title: str = ""
    is_action: bool = False
    location_label: str = ""
    capacity: int | None = None


TEST_PROFILES: list[TestProfileFixture] = [
    TestProfileFixture(
        username="test_river",
        display_name="Test River Chen",
        biography="Mentor and community helper. Happy to share practical tips and cheer people on.",
    ),
    TestProfileFixture(
        username="test_morgan",
        display_name="Test Morgan Lee",
        biography="New member exploring the community. Learning how to ask for and offer help.",
    ),
    TestProfileFixture(
        username="test_sam",
        display_name="Test Sam Ortiz",
        biography="Local action organizer coordinating neighborhood cleanups and volunteer shifts.",
    ),
    TestProfileFixture(
        username="test_jordan",
        display_name="Test Jordan Kim",
        biography="Knowledge sharer who turns useful threads into lasting resources for others.",
    ),
    TestProfileFixture(
        username="test_casey",
        display_name="Test Casey Wells",
        biography="Support-focused member who posts encouragement and small local drives.",
    ),
]

TEST_POSTS: list[TestPostFixture] = [
    TestPostFixture(
        seed_id="river-welcome",
        author_username="test_river",
        body=(
            "Glad to be here. I am sharing a few ways newcomers "
            "can get oriented in the community."
        ),
        kind=PostKind.GENERAL,
        thread_type=ThreadType.DISCUSSION,
    ),
    TestPostFixture(
        seed_id="jordan-knowledge-tip",
        author_username="test_jordan",
        body="When you learn something useful, clip the reply so others can find it later.",
        kind=PostKind.GENERAL,
        thread_type=ThreadType.KNOWLEDGE_SHARE,
        title="A quick tip for preserving helpful answers",
    ),
    TestPostFixture(
        seed_id="morgan-first-post",
        author_username="test_morgan",
        body="Hi everyone — excited to join and learn how this community supports each other.",
        kind=PostKind.GENERAL,
        thread_type=ThreadType.DISCUSSION,
    ),
    TestPostFixture(
        seed_id="casey-encouragement",
        author_username="test_casey",
        body="If today feels heavy, you are not alone. Reach out and tell someone what would help.",
        kind=PostKind.ENCOURAGEMENT_REQUEST,
        thread_type=ThreadType.DISCUSSION,
        is_action=True,
    ),
    TestPostFixture(
        seed_id="morgan-help-moving",
        author_username="test_morgan",
        body=(
            "Need a hand moving boxes this Saturday afternoon. "
            "Two hours of help would make a big difference."
        ),
        kind=PostKind.HELP_REQUEST,
        thread_type=ThreadType.DISCUSSION,
        is_action=True,
        location_label="Downtown",
    ),
    TestPostFixture(
        seed_id="river-help-offer",
        author_username="test_river",
        body="I can help with resume reviews or interview practice this week.",
        kind=PostKind.HELP_OFFER,
        thread_type=ThreadType.DISCUSSION,
        is_action=True,
    ),
    TestPostFixture(
        seed_id="sam-park-cleanup",
        author_username="test_sam",
        body="Join us for a riverside park cleanup this Sunday morning. Gloves and bags provided.",
        kind=PostKind.LOCAL_ACTION,
        thread_type=ThreadType.DISCUSSION,
        is_action=True,
        location_label="Riverside Park",
    ),
    TestPostFixture(
        seed_id="sam-volunteer-shift",
        author_username="test_sam",
        body="Food pantry needs volunteers for a two-hour sorting shift next Wednesday.",
        kind=PostKind.VOLUNTEER_OPPORTUNITY,
        thread_type=ThreadType.DISCUSSION,
        is_action=True,
        capacity=5,
    ),
    TestPostFixture(
        seed_id="casey-local-drive",
        author_username="test_casey",
        body="Collecting shelf-stable food for the neighborhood mutual aid table this weekend.",
        kind=PostKind.LOCAL_ACTION,
        thread_type=ThreadType.DISCUSSION,
        is_action=True,
    ),
]

TEST_REPLIES: list[TestReplyFixture] = [
    TestReplyFixture(
        seed_id="river-welcome-reply-morgan",
        post_seed_id="river-welcome",
        author_username="test_morgan",
        body="Thanks for the warm welcome — glad to be here.",
    ),
    TestReplyFixture(
        seed_id="river-welcome-reply-jordan",
        post_seed_id="river-welcome",
        author_username="test_jordan",
        body="Great intro. I will add a few orientation tips below.",
    ),
    TestReplyFixture(
        seed_id="river-welcome-reply-sam",
        post_seed_id="river-welcome",
        author_username="test_sam",
        body="Welcome! Local action events are a good way to meet people.",
    ),
    TestReplyFixture(
        seed_id="river-welcome-nested-casey",
        post_seed_id="river-welcome",
        author_username="test_casey",
        body="Same here — the community has been really supportive.",
        parent_reply_seed_id="river-welcome-reply-morgan",
    ),
    TestReplyFixture(
        seed_id="jordan-tip-reply-river",
        post_seed_id="jordan-knowledge-tip",
        author_username="test_river",
        body="Clipping replies is one of the best habits here.",
    ),
    TestReplyFixture(
        seed_id="jordan-tip-reply-morgan",
        post_seed_id="jordan-knowledge-tip",
        author_username="test_morgan",
        body="Good tip — I will try clipping the next helpful answer I find.",
    ),
    TestReplyFixture(
        seed_id="morgan-moving-reply-river",
        post_seed_id="morgan-help-moving",
        author_username="test_river",
        body="I can help Saturday afternoon. What time works best?",
    ),
    TestReplyFixture(
        seed_id="morgan-moving-reply-sam",
        post_seed_id="morgan-help-moving",
        author_username="test_sam",
        body="How many boxes are we talking about?",
    ),
    TestReplyFixture(
        seed_id="casey-encouragement-reply-river",
        post_seed_id="casey-encouragement",
        author_username="test_river",
        body="Sending encouragement your way. Reach out anytime.",
    ),
]

TEST_GUILDS: list[TestGuildFixture] = [
    TestGuildFixture(
        seed_id="neighborhood-helpers",
        creator_username="test_river",
        name="Neighborhood Helpers",
        description="A test guild for local mutual aid and practical help.",
        member_usernames=("test_morgan", "test_sam"),
    ),
    TestGuildFixture(
        seed_id="knowledge-circle",
        creator_username="test_jordan",
        name="Knowledge Circle",
        description="A test guild for sharing and preserving useful threads.",
        member_usernames=("test_casey",),
    ),
]
