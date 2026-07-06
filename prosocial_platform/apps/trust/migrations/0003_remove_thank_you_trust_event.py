from django.db import migrations, models


def convert_thank_you_trust_events(apps, schema_editor):
    TrustEvent = apps.get_model("trust", "TrustEvent")
    TrustEvent.objects.filter(event_type="THANK_YOU").update(
        event_type="PROSOCIAL_REACTION",
        source_type="prosocial_reaction",
        source_id="THANKS",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("trust", "0002_functional_trust"),
        ("interactions", "0005_migrate_thank_you_to_reactions"),
    ]

    operations = [
        migrations.RunPython(convert_thank_you_trust_events, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="trustevent",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("PEER_RATING_POSITIVE", "Positive peer rating"),
                    ("PEER_RATING_NEGATIVE", "Negative peer rating"),
                    ("PROSOCIAL_REACTION", "Prosocial reaction"),
                    ("COMMITMENT_VERIFIED", "Commitment verified"),
                    ("CLIP_BY_OTHER", "Content clipped by other"),
                    ("MODERATION_UPHELD", "Report upheld"),
                    ("MODERATION_FRIVOLOUS", "Frivolous report"),
                    ("APPEAL_REVERSAL", "Appeal reversal"),
                ],
                max_length=32,
            ),
        ),
    ]
