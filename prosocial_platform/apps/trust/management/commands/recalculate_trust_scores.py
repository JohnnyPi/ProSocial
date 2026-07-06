from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.trust.services import recalculate_trust_scores

User = get_user_model()


class Command(BaseCommand):
    help = "Recalculate ETS, PTS, and contribution scores for all users."

    def handle(self, *args, **options):
        count = 0
        for user in User.objects.iterator():
            recalculate_trust_scores(user=user)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Recalculated trust scores for {count} users."))
