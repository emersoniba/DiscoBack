from .base import *
from decouple import config

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME_PROD"),
        "USER": config("DB_USER_PROD"),
        "PASSWORD": config("DB_PASSWORD_PROD"),
        "HOST": config("DB_HOST_PROD"),
        "PORT": config("DB_PORT_PROD"),
    }
}

# ==================================================
# CORS
# ==================================================
CORS_ALLOWED_ORIGINS = config(
    "CORS_PROD",
    cast=lambda v: [s.strip() for s in v.split(",")]
)

CORS_ALLOW_CREDENTIALS = True

# ==================================================
# SEGURIDAD
# ==================================================
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True