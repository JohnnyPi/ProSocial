from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save


class ProfilesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.profiles"
    label = "profiles"

    def ready(self):
        from apps.profiles.signals import ensure_profile_on_user_created

        User = get_user_model()
        post_save.connect(ensure_profile_on_user_created, sender=User)
