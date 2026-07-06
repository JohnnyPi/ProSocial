from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class RippleLink(TimeStampedModel):
    helper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ripple_helped",
    )
    helped = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ripple_received",
    )
    source_post = models.ForeignKey(
        "posts.Post", null=True, blank=True, on_delete=models.SET_NULL, related_name="ripple_links"
    )
    citation_note = models.CharField(max_length=500, blank=True)


class CommunitySpotlight(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="spotlights"
    )
    narrative = models.TextField(max_length=5000)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
