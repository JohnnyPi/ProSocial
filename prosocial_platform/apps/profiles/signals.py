from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.profiles.services import ensure_profile_for_user


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile_on_user_created(sender, instance, created, **kwargs):
    if created:
        ensure_profile_for_user(instance)
