import pytest
from django.contrib.auth import get_user_model

from apps.profiles.models import Profile


@pytest.mark.django_db
def test_profile_created_on_user_signal():
    User = get_user_model()
    user = User.objects.create_user(username="signaluser", password="testpass123")
    assert Profile.objects.filter(user=user).exists()
