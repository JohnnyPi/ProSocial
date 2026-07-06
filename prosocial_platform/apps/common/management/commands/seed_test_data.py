from django.core.management.base import BaseCommand

from apps.common.test_data.constants import TEST_MARKER, TEST_PASSWORD
from apps.common.test_data.fixtures import TEST_GUILDS, TEST_POSTS, TEST_PROFILES, TEST_REPLIES
from apps.common.test_data.services import seed_test_data


class Command(BaseCommand):
    help = (
        "Seed test profiles and posts for local development and UI testing. "
        f"All test posts are marked with {TEST_MARKER}. "
        f"Test users share password: {TEST_PASSWORD}"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Print per-record details.",
        )

    def handle(self, *args, **options):
        verbose = options["verbose"]
        if verbose:
            profile_count = len(TEST_PROFILES)
            post_count = len(TEST_POSTS)
            reply_count = len(TEST_REPLIES)
            guild_count = len(TEST_GUILDS)
            self.stdout.write(
                f"Seeding {profile_count} profiles, {post_count} posts, "
                f"{reply_count} replies, and {guild_count} guilds..."
            )

        result = seed_test_data()

        self.stdout.write(
            self.style.SUCCESS(
                "Test data seeded: "
                f"{result.users_created} users created, "
                f"{result.users_updated} users updated, "
                f"{result.posts_created} posts created, "
                f"{result.posts_skipped} posts skipped, "
                f"{result.replies_created} replies created, "
                f"{result.replies_skipped} replies skipped, "
                f"{result.guilds_created} guilds created, "
                f"{result.guilds_skipped} guilds skipped."
            )
        )

        if verbose:
            for fixture in TEST_PROFILES:
                self.stdout.write(f"  profile: {fixture.username} ({fixture.display_name})")
            for fixture in TEST_POSTS:
                self.stdout.write(f"  post: {fixture.seed_id} by {fixture.author_username}")
            for fixture in TEST_REPLIES:
                self.stdout.write(
                    f"  reply: {fixture.seed_id} on {fixture.post_seed_id} "
                    f"by {fixture.author_username}"
                )
            for fixture in TEST_GUILDS:
                self.stdout.write(f"  guild: {fixture.seed_id} ({fixture.name})")
