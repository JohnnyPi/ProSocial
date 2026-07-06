from config.settings.base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "testing-secret-key-not-for-production"

ALLOWED_HOSTS = ["testserver", "localhost"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_prosocial",
        "USER": "prosocial",
        "PASSWORD": "prosocial",
        "HOST": env("POSTGRES_HOST", default="localhost"),  # noqa: F405
        "PORT": env("POSTGRES_PORT", default="5432"),  # noqa: F405
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
