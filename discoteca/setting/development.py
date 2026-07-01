from .base import *
from decouple import config

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME_DEV"),
        "USER": config("DB_USER_DEV"),
        "PASSWORD": config("DB_PASSWORD_DEV"),
        "HOST": config("DB_HOST_DEV"),
        "PORT": config("DB_PORT_DEV"),
    }
}

# ==================================================
# CORS
# ==================================================
CORS_ALLOWED_ORIGINS = config(
    "CORS_DEV",
    cast=lambda v: [s.strip() for s in v.split(",")]
)

CORS_ALLOW_CREDENTIALS = True

# SOLO DESARROLLO
CORS_ALLOW_ALL_ORIGINS = False