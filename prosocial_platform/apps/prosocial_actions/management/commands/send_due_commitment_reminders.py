from django.core.management.base import BaseCommand

from apps.prosocial_actions.services import generate_due_reminders


class Command(BaseCommand):
    help = "Send in-app reminders for due commitments."

    def handle(self, *args, **options):
        count = generate_due_reminders()
        self.stdout.write(self.style.SUCCESS(f"Dispatched {count} reminder(s)."))
