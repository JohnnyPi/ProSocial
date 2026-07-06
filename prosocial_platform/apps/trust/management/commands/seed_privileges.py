from django.core.management.base import BaseCommand

from apps.trust.services import seed_privilege_definitions


class Command(BaseCommand):
    help = "Seed default privilege definitions for earned community abilities."

    def handle(self, *args, **options):
        count = seed_privilege_definitions()
        self.stdout.write(self.style.SUCCESS(f"Seeded {count} new privilege definitions."))
