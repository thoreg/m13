import os
import sys

from .base import *

CORS_ORIGIN_ALLOW_ALL = True

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

INTERNAL_IPS = [
    '127.0.0.1',
]

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

STATIC_ROOT = 'var/static_root/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '..', 'static'),
]

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
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        # print out all sql queries
        # 'django.db': {
        #     'level': 'DEBUG'
        # },
    }
}
