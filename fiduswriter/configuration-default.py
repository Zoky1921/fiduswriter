import os
from pathlib import Path

#############################################
# Django settings for Fidus Writer project. #
#############################################

DEBUG = True

# SOURCE_MAPS - allows any value used by webpack devtool
SOURCE_MAPS = False

# Proyecto base path
BASE_DIR = Path(__file__).resolve().parent
PROJECT_PATH = os.environ.get("PROJECT_PATH", str(BASE_DIR))
SRC_PATH = os.environ.get("SRC_PATH", str(BASE_DIR / "src"))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(PROJECT_PATH, "fiduswriter.sql"),
        "CONN_MAX_AGE": 15,
    }
}

TEST_SERVER = True
CONTACT_EMAIL = "mail@email.com"

ADMINS = [("Your Name", "your_email@example.com")]
MANAGERS = ADMINS

REGISTRATION_OPEN = True
PASSWORD_LOGIN = True
SOCIALACCOUNT_OPEN = True
IS_FREE = True

INSTALLED_APPS = [
    "user_template_manager",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# ✅ ALLOWED_HOSTS desde variable de entorno
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# STATIC y MEDIA
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = os.path.join(PROJECT_PATH, "staticfiles")
MEDIA_ROOT = os.path.join(PROJECT_PATH, "mediafiles")

# SECRET_KEY desde entorno (Render: FIDUSWRITER_SECRET_KEY)
SECRET_KEY = os.environ.get("FIDUSWRITER_SECRET_KEY", "reemplazar-esto-en-producción")
