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
            name="ActivityEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("ACCOUNT_REGISTERED", "Account registered"),
                            ("LOGIN_SUCCEEDED", "Login succeeded"),
                            ("LOGIN_FAILED", "Login failed"),
                            ("PROFILE_UPDATED", "Profile updated"),
                            ("POST_CREATED", "Post created"),
                            ("POST_UPDATED", "Post updated"),
                            ("POST_DELETED", "Post deleted"),
                            ("IMAGE_UPLOAD_REJECTED", "Image upload rejected"),
                        ],
                        max_length=64,
                    ),
                ),
                ("object_type", models.CharField(blank=True, max_length=64)),
                ("object_public_id", models.UUIDField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("request_id", models.CharField(blank=True, max_length=64)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="activity_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="activityevent",
            index=models.Index(
                fields=["event_type", "created_at"], name="common_acti_event_t_aed9aa_idx"
            ),
        ),
    ]
