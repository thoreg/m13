import os

from .base import *

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('PSQL_DB'),
        'USER': os.getenv('PSQL_USER'),
        'PASSWORD': os.getenv('PSQL_PASSWORD'),
        'HOST': os.getenv('PSQL_HOST'),
        'PORT': int(os.getenv('PSQL_PORT')),
    }
}

DEBUG = False
SECRET_KEY = os.getenv('M13_PRODUCTION_DJANGO_SECRET')

STATIC_ROOT = os.getenv('STATIC_ROOT')
