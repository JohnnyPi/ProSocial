import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("body", models.TextField(blank=True, max_length=5000)),
                ("image", models.ImageField(blank=True, upload_to="posts/")),
                ("image_alt_text", models.CharField(blank=True, max_length=255)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "moderation_status",
                    models.CharField(
                        choices=[
                            ("ACTIVE", "Active"),
                            ("HIDDEN", "Hidden"),
                            ("REMOVED", "Removed"),
                        ],
                        default="ACTIVE",
                        max_length=16,
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(fields=["created_at"], name="posts_post_created_870fe2_idx"),
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(
                fields=["author", "created_at"], name="posts_post_author__50f575_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="post",
            index=models.Index(
                fields=["moderation_status", "created_at"], name="posts_post_modera_2a59e9_idx"
            ),
        ),
    ]
