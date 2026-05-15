"""
Minimal Django settings for running simplejwt_multisessions tests.
"""
from datetime import timedelta

SECRET_KEY = 'test-secret-key-for-simplejwt-multisessions-do-not-use-in-prod'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'simplejwt_multisessions',
]

ROOT_URLCONF = 'test_urls'

USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('JWT',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

JWT_MULTISESSIONS = {
    'SECRET': SECRET_KEY,
    'LONG_SESSION': {
        'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
        'ROTATE_REFRESH_TOKENS': False,
        'UPDATE_LAST_LOGIN': False,
        'BLACKLIST_AFTER_ROTATION': False,
        'EXTEND_SESSION': True,
        'EXTEND_SESSION_EVERY_TIME': False,
        'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(days=15),
        'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
        'MAX_NUMBER_ACTIVE_SESSIONS': 5,
        'DESTROY_OLDEST_ACTIVE_SESSION': True,
    },
    'SHORT_SESSION': {
        'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
        'ROTATE_REFRESH_TOKENS': False,
        'UPDATE_LAST_LOGIN': True,
        'BLACKLIST_AFTER_ROTATION': True,
        'EXTEND_SESSION': False,
        'EXTEND_SESSION_EVERY_TIME': False,
        'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(hours=12),
        'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
        'MAX_NUMBER_ACTIVE_SESSIONS': 2,
        'DESTROY_OLDEST_ACTIVE_SESSION': True,
    },
}
