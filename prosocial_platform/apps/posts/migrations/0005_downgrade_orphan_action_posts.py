from django.db import migrations


def downgrade_orphan_action_posts(apps, schema_editor):
    Post = apps.get_model("posts", "Post")
    ActionOpportunity = apps.get_model("prosocial_actions", "ActionOpportunity")
    action_kinds = {
        "HELP_REQUEST",
        "HELP_OFFER",
        "ENCOURAGEMENT_REQUEST",
        "LOCAL_ACTION",
        "VOLUNTEER_OPPORTUNITY",
    }
    linked_post_ids = set(ActionOpportunity.objects.values_list("post_id", flat=True))
    Post.objects.filter(kind__in=action_kinds).exclude(pk__in=linked_post_ids).update(
        kind="GENERAL"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0004_account_deletion_support"),
        ("prosocial_actions", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(downgrade_orphan_action_posts, migrations.RunPython.noop),
    ]
