import os
from pathlib import Path

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-9$y#rs))=6kywmqa$6#$3=)x(8-*0$y!le@*ne#+(j*c$f(g=i"


ALLOWED_HOSTS = []
APPEND_SLASH = True

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = False


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_countries",
    "django_extensions",
    "django_ses",
    "django_pgviews",
    "django_filters",
    "rest_framework",
    "debug_toolbar",
    "mathfilters",
    "corsheaders",
    "massadmin",
    #
    "otto",
    "zalando",
    "etsy",
    "shipping",
    "core",
    "galaxus",
    "galeria",
    "tiktok",
    "aboutyou",
]

MASSEDIT = {
    "ADD_ACTION_GLOBALLY": False,
}

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "m13.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "m13.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "PAGE_SIZE": 100,
}

DEFAULT_FROM_EMAIL = os.getenv("M13_FROM_EMAIL_ADDRESS")
FROM_EMAIL_ADDRESS = os.getenv("M13_FROM_EMAIL_ADDRESS")
SERVER_EMAIL = os.getenv("M13_FROM_EMAIL_ADDRESS")

ADMINS = [
    ("thoreg", "thoreg@gmail.com"),
]
MANAGERS = ADMINS

OTTO_ORDER_CSV_RECEIVER_LIST = [
    "thoreg@gmail.com",
    "custom.art.berlin@googlemail.com",
]

ZALANDO_OEM_WEBHOOK_TOKEN = os.getenv("M13_ZALANDO_OEM_WEBHOOK_TOKEN")
ZALANDO_LOVERS = [
    "thoreg@gmail.com",
    "custom.art.berlin@googlemail.com",
]
ZALANDO_FINANCE_CSV_UPLOAD_PATH = os.path.join(MEDIA_ROOT, "zalando", "finance")
