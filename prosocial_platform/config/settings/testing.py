from config.settings.base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "testing-secret-key-not-for-production"

ALLOWED_HOSTS = ["testserver", "localhost"]

_use_sqlite = env.bool("TEST_USE_SQLITE", default=not env.bool("CI", default=False))  # noqa: F405

if _use_sqlite:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "test_prosocial",
            "USER": "prosocial",
            "PASSWORD": "prosocial",
            "HOST": env("POSTGRES_HOST", default="localhost"),  # noqa: F405
            "PORT": env("POSTGRES_PORT", default="5432"),  # noqa: F405
            "TEST": {"NAME": "test_prosocial"},
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
