TEST_MARKER = "[PROSOCIAL_TEST]"
TEST_EMAIL_DOMAIN = "test.prosocial"
TEST_USERNAME_PREFIX = "test_"
TEST_PASSWORD = "TestPass123!"


def test_email_for_username(username: str) -> str:
    return f"{username}@{TEST_EMAIL_DOMAIN}"


def seed_tag(seed_id: str) -> str:
    return f"{TEST_MARKER}:post={seed_id}"


def reply_seed_tag(seed_id: str) -> str:
    return f"{TEST_MARKER}:reply={seed_id}"


def format_test_body(seed_id: str, text: str) -> str:
    return f"{seed_tag(seed_id)} {text.strip()}"


def format_test_reply_body(seed_id: str, text: str) -> str:
    return f"{reply_seed_tag(seed_id)} {text.strip()}"


def format_test_title(seed_id: str, title: str) -> str:
    return f"{TEST_MARKER}:title={seed_id} {title.strip()}"
