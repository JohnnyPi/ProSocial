from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("moderation", "0002_functional_trust"),
    ]

    operations = [
        migrations.AddField(
            model_name="moderationreview",
            name="is_high_priority",
            field=models.BooleanField(default=False),
        ),
    ]
