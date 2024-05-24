"""
Django settings for boom project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
import environ
import dj_database_url

"""
Hier werden aus der .env.deployment und aus der .env.environment oder
.env.production Variablen ausgelesen, die nicht öffentlich sein dürfen,
wie z.B. Datenbankpasswörter, Secret Keys, etc. Dafür wird die Python
Bibliothek environ verwendet. Die detektiert automatisch Dateien mit
den genannten Namen und liest die Variablen entsprechend aus.
"""
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(".env")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
"""
Der Secret Key ist eine Django interne Variable. Was die genau macht,
habe ich auch keinen Plan, aber es ist wichtig, dass die aus der .env
Datei geladen wird und nicht öffentlich im Github steht
"""
SECRET_KEY = env("SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!
"""
DEBUG ist eine Einstellung, die sagt, wie detailliert Fehlermeldungen
sein sollen. Detaillierte Fehlermeldungen sind gut, wenn man debuggen
möchte, aber unsicher für die Produktion. Deshalb wird im dev environment
DEBUG auf true gesetzt und in Prod auf False. Das wird dann aus der
entsprechenden .env File geladen.
"""
# DEBUG = env("DEBUG")
DEBUG = True

"""
Aus Sicherheitsgründen sollen nicht beliebige Anfragen akzeptiert
werden, sondern nur solche, welche von bekannten IP's oder Domains
kommen. Für die Produktion ist das einfach die URL/IP des Frontend
und für Development der Localhost. Wird entsprechend wieder im env
definiert.
"""
# ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
ALLOWED_HOSTS = ['*']

"""
Das ist sehr ähnlich zu den Allowed Hosts, wir sagen hier noch
zusätzlich, dass wir in der Entwicklung alles erlauben
"""

"""
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')

if env("DJANGO_ENV") == "development":
    CORS_ALLOW_ALL_ORIGINS = True
"""
CORS_ALLOW_ALL_ORIGINS = True

# Application definition
"""
Hier müssen neben den default Apps aus der Bibliothek und
rest_framework und corsheaders auch alle Apps, die man erstellt
hinzufegüt werden, damit sie geladen werden
"""
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "boom.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "boom.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

"""
Es ist üblich in der Entwicklung SQLite zu benuten, weil sehr
lightweight ist, aber dann PostgreSQL in der Produktion zu benutzen.
Hier wird anhand der Environment Variablen entschieden, welches in 
der aktuellen Umgebung benutzt werden soll.
"""
if env("DJANGO_ENV") == "production":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'boomdatabase',
            'USER': 'boomuser',
            'PASSWORD': 'password',
            'HOST': 'db',
            'PORT': '5432',
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "de-de"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True

# CSRF_COOKIE_SECURE = True
# CSRF_TRUSTED_ORIGINS = ['https://api.boomtechnologies.de']


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = os.path.join(BASE_DIR,'static')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"