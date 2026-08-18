"""
Django settings for sms_project (Student Management System).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'sms-dev-secret-key-change-me-before-production-!@#2026'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    '127.0.0.1,localhost,student-management-system-n48c.onrender.com,.onrender.com'
).split(',')

# CSRF: trust the Render domain and localhost (Django 4+ requires this for HTTPS origins)
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    'https://student-management-system-n48c.onrender.com,https://*.onrender.com,http://127.0.0.1:8000,http://localhost:8000'
).split(',')

# SameSite cookie policy — 'Lax' is the safest cross-browser default
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'False') == 'True'
    SESSION_COOKIE_SECURE = os.environ.get('DJANGO_SESSION_COOKIE_SECURE', 'False') == 'True'
    CSRF_COOKIE_SECURE = os.environ.get('DJANGO_CSRF_COOKIE_SECURE', 'False') == 'True'
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', 31536000))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

    if not SECRET_KEY or SECRET_KEY.startswith('django-insecure-'):
        raise RuntimeError('Set a secure DJANGO_SECRET_KEY before running with DEBUG=False.')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party
    'rest_framework',
    'rest_framework.authtoken',

    # Project apps (in build sequence)
    'accounts',
    'academics',
    'students',
    'teachers',
    'attendance',
    'exams',
    'fees',
    'timetable',
    'dashboard',

    # Advanced feature apps
    'notifications',
    'reports',
    'announcements',
    'calendarapp',
    'assignments',
    'library',
    'transport',
    'hostel',
    'parents',
    'auditlog',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise serves static files in production (not needed in local dev)
    *(['whitenoise.middleware.WhiteNoiseMiddleware'] if not DEBUG else []),
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'accounts.middleware.SingleDeviceMiddleware',  # One active session per user
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'sms_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sms_project.wsgi.application'

# ---------------------------------------------------------------------------
# Database
# Priority order:
#   1. DATABASE_URL env var (e.g. a Neon/Postgres connection string) — simplest.
#   2. DJANGO_DB_ENGINE=postgres + individual DJANGO_DB_* vars.
#   3. SQLite fallback, so the project still runs with zero setup.
# See README.md for how to set these.
# ---------------------------------------------------------------------------
import dj_database_url

database_url = os.environ.get('DATABASE_URL')
if database_url:
    DATABASES = {
        'default': dj_database_url.parse(
            database_url,
            conn_max_age=600,
            ssl_require=True,
        )
    }
elif os.environ.get('DJANGO_DB_ENGINE') == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DJANGO_DB_NAME', 'sms_db'),
            'USER': os.environ.get('DJANGO_DB_USER', 'sms_user'),
            'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', 'sms_password'),
            'HOST': os.environ.get('DJANGO_DB_HOST', 'localhost'),
            'PORT': os.environ.get('DJANGO_DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
# WhiteNoise: compress and cache static files with content-hash filenames
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'accounts:login'

# ---------------------------------------------------------------------------
# Session Security
# Session expires when the browser is closed (no persistent cookie).
# Also hard-cap at 8 hours in case the browser stays open all day.
# ---------------------------------------------------------------------------
SESSION_EXPIRE_AT_BROWSER_CLOSE = True   # logout when browser/tab is closed
SESSION_COOKIE_AGE = 8 * 60 * 60        # 8 hours max even if browser stays open
SESSION_SAVE_EVERY_REQUEST = True        # refresh the 8-hour timer on each request
SESSION_COOKIE_HTTPONLY = True           # JS cannot read the session cookie


# ---------------------------------------------------------------------------
# Email (Module: Email Notifications)
# Defaults to printing emails to the console so it works with zero setup.
# For real delivery, set these env vars (e.g. Gmail SMTP, SendGrid, etc.):
#   DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
#   EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS
# ---------------------------------------------------------------------------
EMAIL_BACKEND = os.environ.get('DJANGO_EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@sms.local')

# ---------------------------------------------------------------------------
# SMS (Module: SMS Notifications)
# No SMS gateway is wired up by default (that requires a paid provider
# account like Twilio/MSG91). Messages are logged to the Notification model
# and printed to console via the "console" SMS backend so the feature is
# fully visible and testable without external credentials. To go live, set:
#   SMS_BACKEND=twilio
#   TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER
# ---------------------------------------------------------------------------
SMS_BACKEND = os.environ.get('SMS_BACKEND', 'console')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER', '')

# ---------------------------------------------------------------------------
# WhatsApp (Module: WhatsApp Attendance Notifications)
# Default 'console' logs messages to terminal and Notification history table.
# To send real WhatsApp messages via Twilio, set:
#   WHATSAPP_BACKEND=twilio
#   TWILIO_ACCOUNT_SID=...
#   TWILIO_AUTH_TOKEN=...
#   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
# ---------------------------------------------------------------------------
WHATSAPP_BACKEND = os.environ.get('WHATSAPP_BACKEND', 'console')
TWILIO_WHATSAPP_FROM = os.environ.get('TWILIO_WHATSAPP_FROM', '')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Backup files (Module: Backup/Restore)
BACKUP_ROOT = BASE_DIR / 'backups'
