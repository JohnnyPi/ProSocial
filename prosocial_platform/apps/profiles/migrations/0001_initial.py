import django.db.models.deletion
import django.db.models.functions.text
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("handle", models.CharField(max_length=30, unique=True)),
                ("display_name", models.CharField(blank=True, max_length=100)),
                ("biography", models.TextField(blank=True, max_length=500)),
                ("profile_image", models.ImageField(blank=True, upload_to="profiles/")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="profile",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("handle"),
                name="unique_profile_handle_ci",
            ),
        ),
    ]
