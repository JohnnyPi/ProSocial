import uuid

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Tag(models.Model):
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class PostTag(models.Model):
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="post_tags")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="post_tags")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "tag"], name="unique_post_tag"),
        ]


class ClipKind(models.TextChoices):
    WHOLE_POST = "WHOLE_POST", "Whole post"
    WHOLE_REPLY = "WHOLE_REPLY", "Whole reply"
    WHOLE_THREAD = "WHOLE_THREAD", "Whole thread"
    SELECTION = "SELECTION", "Selection"


class Clip(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="clips"
    )
    post = models.ForeignKey(
        "posts.Post", null=True, blank=True, on_delete=models.CASCADE, related_name="clips"
    )
    reply = models.ForeignKey(
        "interactions.Reply",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="clips",
    )
    clip_kind = models.CharField(max_length=16, choices=ClipKind.choices)
    quoted_text = models.TextField(max_length=5000, blank=True)
    selection_start = models.PositiveIntegerField(null=True, blank=True)
    selection_end = models.PositiveIntegerField(null=True, blank=True)
    private_note = models.TextField(max_length=1000, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["owner", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Clip {self.public_id} by {self.owner_id}"


class CollectionVisibility(models.TextChoices):
    PRIVATE = "PRIVATE", "Private"
    GUILD = "GUILD", "Guild shared"
    PUBLIC = "PUBLIC", "Public"


class Collection(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="collections"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000, blank=True)
    visibility = models.CharField(
        max_length=16,
        choices=CollectionVisibility.choices,
        default=CollectionVisibility.PRIVATE,
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.title


class CollectionItem(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="items")
    clip = models.ForeignKey(
        Clip, null=True, blank=True, on_delete=models.CASCADE, related_name="collection_items"
    )
    post = models.ForeignKey(
        "posts.Post",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="collection_items",
    )
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(clip__isnull=False, post__isnull=True)
                    | models.Q(clip__isnull=True, post__isnull=False)
                ),
                name="collection_item_exactly_one_target",
            ),
            models.UniqueConstraint(
                fields=["collection", "clip"],
                condition=models.Q(clip__isnull=False),
                name="unique_collection_clip",
            ),
            models.UniqueConstraint(
                fields=["collection", "post"],
                condition=models.Q(post__isnull=False),
                name="unique_collection_post",
            ),
        ]
