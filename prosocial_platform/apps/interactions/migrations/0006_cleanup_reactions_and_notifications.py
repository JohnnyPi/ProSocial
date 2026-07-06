from django.db import migrations, models


def map_legacy_reaction_kinds(apps, schema_editor):
    ProsocialReaction = apps.get_model("interactions", "ProsocialReaction")
    ProsocialReaction.objects.filter(kind="CONSTRUCTIVE").update(kind="HELPFUL")
    ProsocialReaction.objects.filter(kind="INSIGHTFUL").update(kind="CLARIFIED")


class Migration(migrations.Migration):
    dependencies = [
        ("interactions", "0005_migrate_thank_you_to_reactions"),
    ]

    operations = [
        migrations.RunPython(map_legacy_reaction_kinds, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="notification",
            name="kind",
            field=models.CharField(
                choices=[
                    ("REPLY_RECEIVED", "Reply received"),
                    ("REPLY_TO_REPLY", "Reply to reply"),
                    ("THANK_YOU_RECEIVED", "Thank you received"),
                    ("COMMITMENT_ACKNOWLEDGED", "Commitment acknowledged"),
                    ("REPORT_RESOLVED", "Report resolved"),
                    ("USER_FOLLOWED", "User followed"),
                    ("POST_FOLLOWED", "Post followed"),
                    ("MESSAGE_RECEIVED", "Message received"),
                    ("GUILD_INVITE", "Guild invite"),
                    ("CHALLENGE_COMPLETED", "Challenge completed"),
                    ("XP_EARNED", "XP earned"),
                    ("MODERATION_ACTION", "Moderation action"),
                    ("CRISIS_REVIEW", "Crisis review"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="prosocialreaction",
            name="kind",
            field=models.CharField(
                choices=[
                    ("HELPFUL", "Helpful"),
                    ("KIND", "Kind"),
                    ("CLARIFIED", "Clarified"),
                    ("SUPPORTIVE", "Supportive"),
                    ("GOOD_FAITH", "Good faith"),
                    ("NEEDS_CONTEXT", "Needs context"),
                    ("THANKS", "Thanks"),
                ],
                max_length=16,
            ),
        ),
    ]
