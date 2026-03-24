import os
import sys
from datetime import timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def env(key, default=None):
    return os.getenv(key, default)


def env_bool(key, default=False):
    value = env(key, str(default))
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def env_int(key, default=0):
    value = env(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def env_list(key, default=""):
    value = env(key, default)
    return [item.strip() for item in str(value).split(",") if item.strip()]


SECRET_KEY = env("DJANGO_SECRET_KEY", "replace-with-a-very-long-random-secret-key-for-dev-only-2026")
DEBUG = env_bool("DJANGO_DEBUG", False)
IS_TESTING = any(arg in {"test", "pytest"} for arg in sys.argv)
IS_RUNSERVER = any(arg.startswith("runserver") for arg in sys.argv)

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0,testserver")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "users",
    "routes",
    "deliveries",
    "tracking",
]

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

ROOT_URLCONF = "api_proyecto.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "api_proyecto.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", "app_proyecto"),
        "USER": env("POSTGRES_USER", "app_user"),
        "PASSWORD": env("POSTGRES_PASSWORD", "admin1234"),
        "HOST": env("POSTGRES_HOST", "localhost"),
        "PORT": env("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": env_int("POSTGRES_CONN_MAX_AGE", 60),
        "OPTIONS": {"sslmode": env("POSTGRES_SSLMODE", "prefer")},
    }
}


AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": env_int("DJANGO_MIN_PASSWORD_LENGTH", 8)},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = env("DJANGO_LANGUAGE_CODE", "es-ec")
TIME_ZONE = env("DJANGO_TIME_ZONE", "America/Guayaquil")

USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_ALL_ORIGINS = env_bool("DJANGO_CORS_ALLOW_ALL", False)
CORS_ALLOWED_ORIGINS = env_list("DJANGO_CORS_ALLOWED_ORIGINS")
CORS_ALLOWED_ORIGIN_REGEXES = env_list(
    "DJANGO_CORS_ALLOWED_ORIGIN_REGEXES",
    r"^http://localhost:\d+$,^http://127\.0\.0\.1:\d+$",
)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": env_int("DJANGO_PAGE_SIZE", 25),
    "EXCEPTION_HANDLER": "api_proyecto.exceptions.custom_exception_handler",
}

if DEBUG:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    )
else:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ("rest_framework.renderers.JSONRenderer",)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env_int("JWT_ACCESS_MINUTES", 30)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env_int("JWT_REFRESH_DAYS", 7)),
    "ROTATE_REFRESH_TOKENS": env_bool("JWT_ROTATE_REFRESH_TOKENS", True),
    "BLACKLIST_AFTER_ROTATION": env_bool("JWT_BLACKLIST_AFTER_ROTATION", True),
    "UPDATE_LAST_LOGIN": True,
}

if not DEBUG and not IS_TESTING and not IS_RUNSERVER:
    SECURE_HSTS_SECONDS = env_int("DJANGO_SECURE_HSTS_SECONDS", 31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
    SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    X_FRAME_OPTIONS = "DENY"
    SECURE_CONTENT_TYPE_NOSNIFF = True
