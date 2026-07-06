from django.db import migrations, models


def rename_thread_type_help_request(apps, schema_editor):
    Post = apps.get_model("posts", "Post")
    Post.objects.filter(thread_type="HELP_REQUEST").update(thread_type="PEER_SUPPORT")


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0005_downgrade_orphan_action_posts"),
    ]

    operations = [
        migrations.RunPython(rename_thread_type_help_request, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="post",
            name="thread_type",
            field=models.CharField(
                choices=[
                    ("DISCUSSION", "Discussion"),
                    ("PEER_SUPPORT", "Peer support thread"),
                    ("KNOWLEDGE_SHARE", "Knowledge share"),
                    ("SUPPORT_CIRCLE", "Support circle"),
                    ("CHALLENGE", "Challenge"),
                ],
                default="DISCUSSION",
                max_length=32,
            ),
        ),
    ]
