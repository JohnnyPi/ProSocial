import environ

from config.settings.base import *  # noqa: F403

env = environ.Env(
    DEBUG=(bool, True),
)

environ.Env.read_env(BASE_DIR / ".env")  # noqa: F405

DEBUG = env.bool("DJANGO_DEBUG", default=True)
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-development-key")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://prosocial:prosocial@localhost:5432/prosocial",
    )
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGGING["loggers"]["django"]["level"] = "DEBUG"  # noqa: F405
