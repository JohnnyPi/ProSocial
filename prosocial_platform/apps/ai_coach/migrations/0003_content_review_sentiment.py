# Generated manually for content review sentiment flow

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("interactions", "0006_cleanup_reactions_and_notifications"),
        ("posts", "0006_rename_thread_type_peer_support"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ai_coach", "0002_functional_trust"),
    ]

    operations = [
        migrations.AddField(
            model_name="sentimentsnapshot",
            name="coaching_summary",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="sentimentsnapshot",
            name="conduct_flags",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="sentimentsnapshot",
            name="confidence",
            field=models.FloatField(default=1.0),
        ),
        migrations.AddField(
            model_name="sentimentsnapshot",
            name="emotion_scores",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.CreateModel(
            name="ContentReviewEvent",
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
                    "surface",
                    models.CharField(
                        choices=[("POST", "Post"), ("REPLY", "Reply"), ("EDIT", "Edit")],
                        max_length=8,
                    ),
                ),
                ("text_hash", models.CharField(max_length=64)),
                ("emotion_scores", models.JSONField(default=dict)),
                ("conduct_flags", models.JSONField(default=list)),
                ("coaching_summary", models.TextField(blank=True)),
                ("coaching_tips", models.JSONField(default=list)),
                ("tone_summary", models.TextField(blank=True)),
                (
                    "label",
                    models.CharField(
                        choices=[
                            ("POSITIVE", "Positive"),
                            ("NEUTRAL", "Neutral"),
                            ("NEGATIVE", "Negative"),
                        ],
                        default="NEUTRAL",
                        max_length=16,
                    ),
                ),
                ("score", models.FloatField(default=0.0)),
                ("model_version", models.CharField(default="nrc-v1", max_length=32)),
                ("edited_after_review", models.BooleanField(default=False)),
                ("is_finalized", models.BooleanField(default=False)),
                ("is_consumed", models.BooleanField(default=False)),
                (
                    "post",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="content_review_events",
                        to="posts.post",
                    ),
                ),
                (
                    "reply",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="content_review_events",
                        to="interactions.reply",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="content_review_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
