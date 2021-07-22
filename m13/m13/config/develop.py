from .base import *



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'm13',
        'USER': 'postgres',
        'PASSWORD': 'local',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

DEBUG = True
