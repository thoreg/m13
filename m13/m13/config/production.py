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

EMAIL_BACKEND = 'django_ses.SESBackend'

AWS_ACCESS_KEY_ID = os.getenv('M13_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('M13_AWS_SECRET_ACCESS_KEY')

LOG_DIR = os.getenv('M13_LOG_DIR', '/var/log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{LOG_DIR}/django/m13/default.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{LOG_DIR}/django/m13/requests.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        '': {
            # 'handlers': ['default', 'mail_admins'],
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {  # Stop SQL debug from logging to main logger
            # 'handlers': ['request_handler', 'mail_admins'],
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}
