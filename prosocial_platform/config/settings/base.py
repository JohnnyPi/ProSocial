from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.common",
    "apps.accounts",
    "apps.profiles",
    "apps.posts",
    "apps.dashboard",
    "apps.interactions",
    "apps.prosocial_actions",
    "apps.knowledge",
    "apps.follows",
    "apps.guilds",
    "apps.messaging",
    "apps.trust",
    "apps.gamification",
    "apps.ai_coach",
    "apps.moderation",
    "apps.engagement",
    "apps.discovery",
    "apps.advanced",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.profiles.middleware.ensure_user_profile",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.common.context_processors.shell_context",
                "apps.common.context_processors.functional_trust_context",
                "apps.posts.context_processors.feed_filters",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "accounts:login"

# Content limits
POST_BODY_MAX_LENGTH = 5000
PROFILE_BIO_MAX_LENGTH = 500
HANDLE_MIN_LENGTH = 3
HANDLE_MAX_LENGTH = 30
DISPLAY_NAME_MAX_LENGTH = 100

# Image upload limits
IMAGE_MAX_BYTES = 5 * 1024 * 1024
IMAGE_MAX_WIDTH = 4096
IMAGE_MAX_HEIGHT = 4096
IMAGE_MAX_PIXELS = 16_000_000
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}

# Rate limiting (attempts per window)
REGISTRATION_RATE_LIMIT = 5
REGISTRATION_RATE_WINDOW_SECONDS = 3600
LOGIN_RATE_LIMIT = 10
LOGIN_RATE_WINDOW_SECONDS = 900
EXPORT_RATE_LIMIT = 3
EXPORT_RATE_WINDOW_SECONDS = 3600
ACCOUNT_DELETION_GRACE_DAYS = 30

FUNCTIONAL_TRUST_FEATURES = {
    "prosocial_reactions": True,
    "civility_prompts": True,
    "content_review": True,
    "sentiment_llm_enhancement": False,
    "moderation_actions": True,
    "moderation_appeals": True,
    "assurance_profile": True,
    "earned_privileges": True,
    "scoped_endorsements": True,
    "context_notes": True,
    "anti_gaming": True,
}

APPEAL_WINDOW_DAYS = 14

SENTIMENT_LLM_PROVIDER = env("SENTIMENT_LLM_PROVIDER", default="")
SENTIMENT_LLM_API_KEY = env("SENTIMENT_LLM_API_KEY", default="")
SENTIMENT_LLM_TIMEOUT_SECONDS = env.int("SENTIMENT_LLM_TIMEOUT_SECONDS", default=5)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
