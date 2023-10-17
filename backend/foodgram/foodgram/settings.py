import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

USE_SQLITE = os.getenv('USE_SQLITE')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'secret_key_name')

DEBUG = os.getenv('DEBUG')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1').split()

CSRF_TRUSTED_ORIGINS = ['https://51.250.100.142']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql' if USE_SQLITE is None else 'django.db.backends.sqlite3',
        'NAME': os.getenv('POSTGRES_DB', 'django') if USE_SQLITE is None else 'sqlite_db.bak',
        'USER': os.getenv('POSTGRES_USER', 'django') if USE_SQLITE is None else '',
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', '') if USE_SQLITE is None else '',
        'HOST': os.getenv('DB_HOST', 'db') if USE_SQLITE is None else '',
        'PORT': os.getenv('DB_PORT', 5432) if USE_SQLITE is None else '',
    }
}

PASSWORD_VALIDATION_USER = (
    'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
)

PASSWORD_VALIDATION_MINIMUM = (
    'django.contrib.auth.password_validation.MinimumLengthValidator'
)
PASSWORD_VALIDATION_COMMON = (
    'django.contrib.auth.password_validation.CommonPasswordValidator'
)
PASSWORD_VALIDATION_NUMERIC = (
    'django.contrib.auth.password_validation.NumericPasswordValidator'
)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': PASSWORD_VALIDATION_USER,
    },
    {
        'NAME': PASSWORD_VALIDATION_MINIMUM,
    },
    {
        'NAME': PASSWORD_VALIDATION_COMMON,
    },
    {
        'NAME': PASSWORD_VALIDATION_NUMERIC,
    },
]

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/backend_static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/backend_media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.CustomUser'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "PERMISSIONS": {
        "user": ["rest_framework.permissions.IsAuthenticated"],
        "user_list": ["rest_framework.permissions.AllowAny"],
    },
    "SERIALIZERS": {
        "user": "api.serializers.CustomUserSerializer",
        "current_user": "api.serializers.CustomUserSerializer",
        "user_create": "api.serializers.CustomUserCreateSerializer",
    },
    "HIDE_USERS": False,
}
