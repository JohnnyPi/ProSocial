from django.core.management.base import BaseCommand, CommandError

from apps.common.test_data.services import purge_test_data


class Command(BaseCommand):
    help = "Remove all test profiles, posts, and related data from the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many records would be deleted without deleting.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Allow purge when DEBUG=False.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        force = options["force"]

        try:
            result = purge_test_data(dry_run=dry_run, force=force)
        except RuntimeError as exc:
            raise CommandError(str(exc)) from exc

        prefix = "Would delete" if dry_run else "Deleted"
        self.stdout.write(
            self.style.SUCCESS(
                f"{prefix} {result.users_deleted} test users and "
                f"{result.orphan_posts_deleted} orphan test posts."
            )
        )
