from django.db import migrations, models


def mark_self_asserted_verified(apps, schema_editor):
    ScopedEndorsement = apps.get_model("profiles", "ScopedEndorsement")
    ScopedEndorsement.objects.filter(verification_method="SELF_ASSERTED").update(status="VERIFIED")


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0003_functional_trust"),
    ]

    operations = [
        migrations.AddField(
            model_name="scopedendorsement",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("VERIFIED", "Verified"),
                    ("REJECTED", "Rejected"),
                ],
                default="PENDING",
                max_length=16,
            ),
        ),
        migrations.RunPython(mark_self_asserted_verified, migrations.RunPython.noop),
    ]
