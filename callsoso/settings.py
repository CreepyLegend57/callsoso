"""
Django settings for callsoso project.
Production-ready, host-agnostic configuration.
"""

from pathlib import Path
import os

# ======================================================
# BASE DIRECTORY
# ======================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================================
# ENVIRONMENT VARIABLES
# ======================================================
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-local-dev-only-change-in-production"
)

DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")

# ======================================================
# APPLICATION DEFINITION
# ======================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local apps
    "website",
    "directory",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "callsoso.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "callsoso.wsgi.application"

# ======================================================
# DATABASE
# ======================================================
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DJANGO_DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DJANGO_DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DJANGO_DB_USER", ""),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", ""),
        "HOST": os.getenv("DJANGO_DB_HOST", ""),
        "PORT": os.getenv("DJANGO_DB_PORT", ""),
    }
}

# ======================================================
# PASSWORD VALIDATION
# ======================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ======================================================
# INTERNATIONALIZATION
# ======================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Harare"
USE_I18N = True
USE_TZ = True

# ======================================================
# STATIC & MEDIA FILES
# ======================================================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ======================================================
# DEFAULT PRIMARY KEY
# ======================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ======================================================
# EMAIL
# ======================================================
EMAIL_BACKEND = os.getenv("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("DJANGO_EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("DJANGO_EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("DJANGO_EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("DJANGO_EMAIL_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("DJANGO_EMAIL_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.getenv("DJANGO_DEFAULT_FROM_EMAIL", "Call Soso <noreply@callsoso.org>")
CONTACT_EMAIL = os.getenv("DJANGO_CONTACT_EMAIL", "info@callsoso.org")

# ======================================================
# AUTHENTICATION (Namespace-safe)
# ======================================================
LOGIN_URL = os.getenv("DJANGO_LOGIN_URL", "website:login")
LOGIN_REDIRECT_URL = os.getenv("DJANGO_LOGIN_REDIRECT_URL", "directory:directory_home")
LOGOUT_REDIRECT_URL = os.getenv("DJANGO_LOGOUT_REDIRECT_URL", "website:home")

# ======================================================
# SECURITY SETTINGS
# ======================================================
if not DEBUG:
    # Production-level security
    SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "True") == "True"
    SESSION_COOKIE_SECURE = os.getenv("DJANGO_SESSION_COOKIE_SECURE", "True") == "True"
    CSRF_COOKIE_SECURE = os.getenv("DJANGO_CSRF_COOKIE_SECURE", "True") == "True"
    SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", 3600))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", "True") == "True"
    SECURE_HSTS_PRELOAD = os.getenv("DJANGO_SECURE_HSTS_PRELOAD", "True") == "True"
    SECURE_BROWSER_XSS_FILTER = os.getenv("DJANGO_SECURE_BROWSER_XSS_FILTER", "True") == "True"
    SECURE_CONTENT_TYPE_NOSNIFF = os.getenv("DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", "True") == "True"
    X_FRAME_OPTIONS = os.getenv("DJANGO_X_FRAME_OPTIONS", "DENY")
else:
    # Local development: disable HTTPS enforcement
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
