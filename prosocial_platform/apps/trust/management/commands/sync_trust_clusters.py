from django.core.management.base import BaseCommand

from apps.trust.clusters import sync_trust_clusters


class Command(BaseCommand):
    help = "Recompute trust clusters from guild membership and follow graph."

    def handle(self, *args, **options):
        count = sync_trust_clusters()
        self.stdout.write(self.style.SUCCESS(f"Updated {count} user cluster assignments."))
