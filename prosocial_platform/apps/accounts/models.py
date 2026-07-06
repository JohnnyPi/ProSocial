import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField("email address", unique=True)

    REQUIRED_FIELDS = ["email"]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower("email"),
                name="unique_user_email_ci",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username
