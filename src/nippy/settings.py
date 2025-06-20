"""
Django settings for nippy project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

BOOL_TUPLE = ("true", "1", "t")

from os import environ
from pathlib import Path


# Uploading settings
MAXIMUM_VIDEO_SIZE_BYTES = eval(
    environ.get("MAXIMUM_VIDEO_SIZE_BYTES", "3 * 1024 * 1024 * 1024")
)
CHUNK_SIZE_BYTES = eval(environ.get("CHUNK_SIZE_BYTES", "20 * 1000 * 1024"))
TOTAL_CHUNKS = eval(environ.get("TOTAL_CHUNKS", "3000/20"))
MAXIMUM_VIDEO_DURATION = eval(environ.get("MAXIMUM_VIDEO_DURATION", "10 * 60"))
FFMPEG_PATH = environ.get("FFMPEG_PATH", "ffmpeg")
FFPROBE_PATH = environ.get("FFPROBE_PATH", "ffprobe")
MASTER_PASSWORD = environ.get("MASTER_PASSWORD", "nip::24")
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ.get(
    "SECRET_KEY", "django-insecure-%e4v_b+s!0_@o6!+!^bz1zo^e0)6dkawcg5b8p!co5)q9o+xcv"
)
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = environ.get("DEBUG", "True").lower() in ("true", "1", "t")

DJANGO_VITE = {"default": {"dev_mode": DEBUG}}


ALLOWED_HOSTS = environ.get("ALLOWED_HOSTS", "*").split(", ")
CSRF_TRUSTED_ORIGINS = (
    environ.get("CSRF_TRUSTED_ORIGINS", "").split(", ")
    if environ.get("CSRF_TRUSTED_ORIGINS", [])
    else []
)
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "huey.contrib.djhuey",
    "django_vite",
    "core",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]
if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

MIDDLEWARE += [
    "core.middleware.AppMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]


ROOT_URLCONF = "nippy.urls"

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
                "core.context_processors.custom_context",
            ],
            "builtins": [
                "django.templatetags.static",
                "django.contrib.humanize.templatetags.humanize",
                "core.templatetags.filters",
            ],
        },
    },
]

WSGI_APPLICATION = "nippy.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": environ.get("DEFAULT_DB_NAME", "nippy"),
        "USER": environ.get("DEFAULT_DB_USER", "postgres"),
        "PASSWORD": environ.get("DEFAULT_DB_PWD", "postgres"),
        "HOST": environ.get("DEFAULT_DB_HOST", "localhost"),
        "PORT": environ.get("DEFAULT_DB_PORT", ""),
    }
}

AUTH_USER_MODEL = "core.User"
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

INTERNAL_IPS = environ.get("INTERNAL_IPS", "127.0.0.1").split(", ")

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

NIPPY_BASE_DIR = Path(__file__).resolve().parent.parent.parent


PUBLIC_ROOT = NIPPY_BASE_DIR / "public"

STATIC_URL = "static/"

STATIC_ROOT = PUBLIC_ROOT / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = PUBLIC_ROOT / "media"

STATICFILES_DIRS = [
    BASE_DIR / "dist",
]

if DEBUG:
    STATICFILES_DIRS.append(BASE_DIR / "assets" / "public")
    STATICFILES_DIRS.append(BASE_DIR / "assets")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

HUEY = {
    "huey_class": "huey.contrib.sql_huey.SqlHuey",  # Huey implementation to use.
    "name": DATABASES["default"]["NAME"],  # Use db name for huey.
    "results": True,  # Store return values of tasks.
    "store_none": False,  # If a task returns None, do not save to results.
    "immediate": False,  # If DEBUG=True, run synchronously.
    "utc": True,  # Use UTC for all times internally.
    "blocking": True,  # Perform blocking pop rather than poll Redis.
    "connection": {
        "database": f"postgresql://{DATABASES['default']['USER']}:{DATABASES['default']['PASSWORD']}@{DATABASES['default']['HOST']}:{DATABASES['default']['PORT']}/{DATABASES['default']['NAME']}",
        "read_timeout": 1,
    },
    "consumer": {
        "workers": 2,
        "worker_type": "thread",
        "initial_delay": 0.1,  # Smallest polling interval, same as -d.
        "backoff": 1.15,  # Exponential backoff using this rate, -b.
        "max_delay": 10.0,  # Max possible polling interval, -m.
        "scheduler_interval": 3,  # Check schedule every second, -s.
        "periodic": True,  # Enable crontab feature.
        "check_worker_health": True,  # Enable worker health checks.
        "health_check_interval": 1,  # Check worker health every second.
    },
}
