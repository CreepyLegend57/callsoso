"""
Django settings for callsoso project.
Updated for future-proof deployment to any host.
"""

from pathlib import Path
import os

# ===========================
# BASE DIRECTORY
# ===========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================
# SECRET KEY & DEBUG
# ===========================
# Use environment variable for security in production
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-placeholder-key')
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

# ===========================
# ALLOWED HOSTS
# ===========================
# Accept all hosts by default, can override with environment variable
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')

# ===========================
# APPLICATION DEFINITION
# ===========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'website',
    'directory',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'callsoso.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'callsoso.wsgi.application'

# ===========================
# DATABASE
# ===========================
# Use environment variables to switch easily to Postgres, MySQL, etc.
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DJANGO_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DJANGO_DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DJANGO_DB_USER', ''),
        'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', ''),
        'HOST': os.getenv('DJANGO_DB_HOST', ''),
        'PORT': os.getenv('DJANGO_DB_PORT', ''),
    }
}

# ===========================
# PASSWORD VALIDATION
# ===========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===========================
# INTERNATIONALIZATION
# ===========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Harare'
USE_I18N = True
USE_TZ = True

# ===========================
# STATIC FILES
# ===========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # collectstatic target for production

# ===========================
# MEDIA FILES
# ===========================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ===========================
# DEFAULT AUTO FIELD
# ===========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================
# EMAIL SETTINGS
# ===========================
EMAIL_BACKEND = os.getenv('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('DJANGO_EMAIL_HOST', 'smtp.yourprovider.com')
EMAIL_PORT = int(os.getenv('DJANGO_EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('DJANGO_EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_USER', 'your_email@example.com')
EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_PASSWORD', 'your_password')
DEFAULT_FROM_EMAIL = os.getenv('DJANGO_DEFAULT_FROM_EMAIL', 'Call Soso <noreply@callsoso.org>')
CONTACT_EMAIL = os.getenv('DJANGO_CONTACT_EMAIL', 'info@callsoso.org')

# ===========================
# AUTHENTICATION
# ===========================
LOGIN_URL = os.getenv('DJANGO_LOGIN_URL', 'login')
LOGIN_REDIRECT_URL = os.getenv('DJANGO_LOGIN_REDIRECT_URL', 'directory_home')
LOGOUT_REDIRECT_URL = os.getenv('DJANGO_LOGOUT_REDIRECT_URL', 'login')

# ===========================
# SECURITY (production-ready)
# ===========================
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
