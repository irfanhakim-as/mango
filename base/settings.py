"""
Django settings for base project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path


##################################################################
# CONFIGURATIONS
##################################################################

COMPULSORY_SETTINGS = list(
    setting.strip() for setting in os.getenv('COMPULSORY_SETTINGS',
    'SECRET_KEY, ALLOWED_HOSTS, BOT_ID, ACCESS_TOKEN, API_BASE_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CELERY_TIMEZONE'
    ).split(',')
)
BOT_ID = os.getenv('BOT_ID', 'mango')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', '/base/base/mastodon.secret')
API_BASE_URL = os.getenv('API_BASE_URL', 'https://botsin.space/')


##################################################################
# Celery Settings
##################################################################

CELERY_BROKER_URL = os.getenv('CELERY_BROKER', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_BACKEND', 'redis://localhost:6379/0')
CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE', 'Asia/Kuala_Lumpur')


##################################################################
# Database Settings
##################################################################

DB_TYPE = os.getenv('DB_TYPE', 'postgresql') # database type
DB_NAME = os.getenv('DB_NAME') # database name
DB_USER = os.getenv('DB_USER') # database username
DB_PASS = os.getenv('DB_PASS') # database password
DB_HOST = os.getenv('DB_HOST') # database host
DB_PORT = int(os.getenv('DB_PORT', '5432')) # database port


# ================= DO NOT EDIT BEYOND THIS LINE =================


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG',False) == 'true'

ALLOWED_HOSTS = list(os.getenv('ALLOWED_HOSTS','*').split(','))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'base.apps.BaseConfig',
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

ROOT_URLCONF = 'base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'base.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % DB_TYPE,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging
# https://docs.djangoproject.com/en/3.2/topics/logging/

LOGGING = {
    'version': 1,
    'loggers': {
        'base':{
            'handlers':['info','warning','error'],
            'level':'DEBUG'
        }
    },
    'handlers': {
        'info': {
            'level':'INFO',
            'class':'logging.FileHandler',
            'filename':'/var/log/apache2/info.log',
            'formatter':'verbose',
        },
        'warning': {
            'level':'WARNING',
            'class':'logging.FileHandler',
            'filename':'/var/log/apache2/warning.log',
            'formatter':'verbose',
        },
        'error': {
            'level':'ERROR',
            'class':'logging.FileHandler',
            'filename':'/var/log/apache2/error.log',
            'formatter':'verbose',
        },
    },
    'formatters': {
        'standard':{
            'format':'{levelname}|{asctime}|{module}|{process:d}|{thread:d}|{message}',
            'style':'{',
        },
        'verbose':{
            'format':'{levelname}|{asctime}|{module}|{funcName}|{lineno:d}|{message}',
            'style':'{',
        }
    }
}
