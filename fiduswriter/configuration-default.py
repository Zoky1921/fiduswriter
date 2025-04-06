import os
from pathlib import Path

#############################################
# Django settings for Fidus Writer project. #
#############################################

DEBUG = True

# SOURCE_MAPS - allows any value used by webpack devtool
SOURCE_MAPS = False

# Proyecto base path (mejor con Pathlib para mayor robustez)
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

# Aplicaciones instaladas (puedes agregar más si las necesitas)
INSTALLED_APPS = [
    "user_template_manager",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

# Si usás HTTPS y querés usar login por redes sociales
# ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

# Si necesitás habilitar CORS o CSRF desde otros dominios
# CSRF_TRUSTED_ORIGINS = ["https://tu-dominio.com"]

# Tamaño máximo de imágenes subidas por usuarios (deshabilitado)
MEDIA_MAX_SIZE = False

# STATIC y MEDIA
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = os.path.join(PROJECT_PATH, "staticfiles")
MEDIA_ROOT = os.path.join(PROJECT_PATH, "mediafiles")

# Configuración de email (si se envían notificaciones)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.tu-dominio.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'usuario'
# EMAIL_HOST_PASSWORD = 'contraseña'
# DEFAULT_FROM_EMAIL = 'noreply@tu-dominio.com'

# SECRET_KEY obligatoria para Django
SECRET_KEY = os.environ.get("SECRET_KEY", "reemplazar-esto-por-una-real-en-producción")
