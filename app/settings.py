"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import os

from celery.schedules import crontab
from . import env_variable

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

SECRET_KEY = env_variable("secret_key", "REALLY-INSECURE-KEY-FOR-TESTS")


if env_variable("CI", False):
    print("forcing debug mode for CI")
    DEBUG = True
else:
    DEBUG = env_variable("django_debug", False) == "True"

print(f"starting with debug: {DEBUG}")

ALLOWED_HOSTS = env_variable("allowed_hosts", "127.0.0.1 localhost").split()
INTERNAL_IPS = env_variable("internal_ips", "127.0.0.1 localhost").split()

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "django_filters",
    "django_celery_results",
    "social_django",
    "utils",
    "profiles",
    "novels",
    "scrapes",
]
if DEBUG:
    INSTALLED_APPS.insert(6, "debug_toolbar")

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
            "debug": DEBUG,
        },
    }
]

if DEBUG:
    TEMPLATES[0]["OPTIONS"]["context_processors"].insert(
        0, "django.template.context_processors.debug"
    )

WSGI_APPLICATION = "app.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env_variable("database_name", "django"),
        "USER": env_variable("database_user", "django"),
        "PASSWORD": env_variable("database_pass", "django"),
        "HOST": env_variable("database_host", "database"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    # },
    # {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    # {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    # {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "profiles.User"


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGGING = {
    "version": 1,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": True},
        "scrapes.tasks": {"handlers": ["console"], "level": "INFO", "propagate": True},
    },
}

AUTHENTICATION_BACKENDS = (
    "social_core.backends.github.GithubOAuth2",
    "django.contrib.auth.backends.ModelBackend",
    "profiles.backends.TokenAuthBackend",
)

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "scrapes:home"
SOCIAL_AUTH_GITHUB_KEY = env_variable("github_auth_key", "unknown")
SOCIAL_AUTH_GITHUB_SECRET = env_variable("github_auth_secret", "unknown")
SOCIAL_AUTH_POSTGRES_JSONFIELD = True

if (
    SOCIAL_AUTH_GITHUB_KEY == "unknown" or SOCIAL_AUTH_GITHUB_SECRET == "unknown"
):  # pragma: no cover
    print("logging in won't be possible without github auth")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = "static_root/"

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "node_modules"),
]


CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": "redis://cache:6379/3",
        "KEY_PREFIX": "django_",
    },
    "pages": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": "redis://cache:6379/3",
        "KEY_PREFIX": "pages_",
    },
}

GENERIC_CACHE_TIME = 60 * 15
if DEBUG:
    GENERIC_CACHE_TIME = 5

if GENERIC_CACHE_TIME > 60:
    cache_msg=f"{GENERIC_CACHE_TIME/60}m"
else:
    cache_msg=f"{GENERIC_CACHE_TIME}s"
print(f"caching for {cache_msg} where applicable")


SESSION_ENGINE = "django.contrib.sessions.backends.cache"


CELERY_BROKER_URL = env_variable("cache", "redis://cache:6379") + "/1"
CELERY_RESULTS_BACKEND = env_variable("results", "django-db")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"

CELERY_BEAT_SCHEDULE = {
    "minutely_fetch": {
        "task": "scrapes.tasks.fetch_content",
        "schedule": crontab(minute="*"),
    },
    "generators": {
        "task": "scrapes.tasks.generators_task",
        "schedule": crontab(minute="*/5"),
    },
    "parsers": {
        "task": "scrapes.tasks.parsers_task",
        "schedule": crontab(minute="*/5"),
    },
}

GRAPHENE = {"SCHEMA": "app.schema.schema"}  # Where your Graphene schema lives

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
}

CORS_ORIGIN_WHITELIST = env_variable("cors_whitelist", "").split()
