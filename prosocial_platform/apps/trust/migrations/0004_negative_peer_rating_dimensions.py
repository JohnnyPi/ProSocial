from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trust", "0003_remove_thank_you_trust_event"),
    ]

    operations = [
        migrations.AlterField(
            model_name="peerrating",
            name="dimension",
            field=models.CharField(
                choices=[
                    ("ESCALATORY", "Escalatory"),
                    ("DISMISSIVE", "Dismissive"),
                    ("SPAMMY", "Spammy"),
                ],
                max_length=16,
            ),
        ),
    ]
