from django.core.management.base import BaseCommand

from apps.accounts.services import process_due_account_deletions


class Command(BaseCommand):
    help = "Process account deletion requests that have passed their grace period."

    def handle(self, *args, **options):
        count = process_due_account_deletions()
        self.stdout.write(self.style.SUCCESS(f"Processed {count} account deletion(s)."))
