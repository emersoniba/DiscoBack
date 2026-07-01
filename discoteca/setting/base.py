import os
from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ==================================================
# ENTORNO
# ==================================================
ENV = config("DJANGO_ENV", default="development")

IS_DEV = ENV == "development"
IS_PROD = ENV == "production"

# ==================================================
# SEGURIDAD
# ==================================================
SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=lambda v: [s.strip() for s in v.split(",")]
)

# ==================================================
# APPS
# ==================================================
APP_BASE = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

APP_TRIRD = [
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
    "rest_framework_simplejwt.token_blacklist",
]

APP_LOCAL = [
    "modulos.utilitario",
    "modulos.users",
    "modulos.inventario",
]

INSTALLED_APPS = APP_BASE + APP_TRIRD + APP_LOCAL

# ==================================================
# MIDDLEWARE
# ==================================================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'discoteca.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = 'discoteca.wsgi.application'

# ==================================================
# AUTH
# ==================================================
AUTH_USER_MODEL = "users.Usuario"

# ==================================================
# REST FRAMEWORK
# ==================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ==================================================
# JWT
# ==================================================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ==================================================
# SWAGGER
# ==================================================
SPECTACULAR_SETTINGS = {
    "TITLE": "Api Discoteca",
    "DESCRIPTION": "Sistema de gestión",
    "VERSION": "1.0.0",
}

# ==================================================
# INTERNACIONALIZACIÓN
# ==================================================
LANGUAGE_CODE = "es-bo"
TIME_ZONE = "America/La_Paz"

USE_I18N = True
USE_TZ = True

# ==================================================
# STATIC / MEDIA
# ==================================================
STATIC_URL = "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"