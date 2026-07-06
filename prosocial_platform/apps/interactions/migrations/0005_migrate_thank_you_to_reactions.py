from django.db import migrations

THANKS_CATEGORY = "support"


def migrate_thank_yous_to_reactions(apps, schema_editor):
    ThankYou = apps.get_model("interactions", "ThankYou")
    ProsocialReaction = apps.get_model("interactions", "ProsocialReaction")

    for thank_you in ThankYou.objects.iterator():
        if thank_you.post_id:
            exists = ProsocialReaction.objects.filter(
                sender_id=thank_you.sender_id,
                post_id=thank_you.post_id,
                kind="THANKS",
            ).exists()
            if exists:
                continue
            ProsocialReaction.objects.create(
                sender_id=thank_you.sender_id,
                post_id=thank_you.post_id,
                reply_id=None,
                kind="THANKS",
                category=THANKS_CATEGORY,
                created_at=thank_you.created_at,
                updated_at=thank_you.updated_at,
            )
        elif thank_you.reply_id:
            exists = ProsocialReaction.objects.filter(
                sender_id=thank_you.sender_id,
                reply_id=thank_you.reply_id,
                kind="THANKS",
            ).exists()
            if exists:
                continue
            ProsocialReaction.objects.create(
                sender_id=thank_you.sender_id,
                post_id=None,
                reply_id=thank_you.reply_id,
                kind="THANKS",
                category=THANKS_CATEGORY,
                created_at=thank_you.created_at,
                updated_at=thank_you.updated_at,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("interactions", "0004_functional_trust"),
    ]

    operations = [
        migrations.RunPython(migrate_thank_yous_to_reactions, migrations.RunPython.noop),
    ]
