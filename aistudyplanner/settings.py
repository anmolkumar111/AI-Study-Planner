"""
AIStudyPlanner - Django Settings
=================================
Main configuration file for the AIStudyPlanner project.
This file controls database, apps, templates, static files, and more.
"""

from pathlib import Path

# ─────────────────────────────────────────────
# BASE DIRECTORY — root of the project folder
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────
# SECURITY KEY — keep secret in production!
# ─────────────────────────────────────────────
SECRET_KEY = 'django-insecure-aistudyplanner-secret-key-change-in-production-xyz123'

# In production set DEBUG = False
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'ai-study-planner-sigma.vercel.app', '.vercel.app']

# ─────────────────────────────────────────────
# INSTALLED APPS — all Django + custom apps
# ─────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',          # Built-in authentication
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'planner',                      # Our main application
]

# ─────────────────────────────────────────────
# MIDDLEWARE — request/response processing layers
# ─────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ─────────────────────────────────────────────
# URL CONFIGURATION
# ─────────────────────────────────────────────
ROOT_URLCONF = 'aistudyplanner.urls'

# ─────────────────────────────────────────────
# TEMPLATES — HTML template settings
# ─────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Global templates folder
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

WSGI_APPLICATION = 'aistudyplanner.wsgi.application'

# ─────────────────────────────────────────────
# DATABASE — SQLite (default, no setup needed)
# ─────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─────────────────────────────────────────────
# PASSWORD VALIDATORS
# ─────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────
# LANGUAGE & TIMEZONE
# ─────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'   # IST timezone
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────
# STATIC FILES — CSS, JS, Images
# ─────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # Our custom static folder

# ─────────────────────────────────────────────
# DEFAULT PRIMARY KEY
# ─────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────────────────────────────
# AUTHENTICATION REDIRECTS
# ─────────────────────────────────────────────
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# ─────────────────────────────────────────────
# MESSAGE TAGS — for styled flash messages
# ─────────────────────────────────────────────
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}
