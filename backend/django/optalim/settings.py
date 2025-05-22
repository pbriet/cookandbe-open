# Django settings for optalim project.

import os
import sys
import json
import logging
from corsheaders.defaults import default_headers

DEBUG = os.environ.get('DEBUG', 'False') == 'True'
DEBUG_LOGS_DIR = '/logs'
DEBUG_TOOLBAR_ENABLED = DEBUG and 'DJANGO_TOOLBAR' in os.environ
DEBUG_TOOLBAR_PATCH_SETTINGS = False
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev").lower()

# Is the current execution a test ?
TESTING = bool(ENVIRONMENT == "test")
TESTING_WITH_PGSQL = len(sys.argv) > 1 and sys.argv[1] == "test_prod"
TESTING_WITH_PGSQL = TESTING_WITH_PGSQL or ("optest" in sys.argv and "--pgsql" in sys.argv)
ENABLE_MONGO_TESTING = os.environ.get('ENABLE_MONGO_TESTING', 'False') == 'True'

ADMINS = (
    ('Pascal BRIET', 'elkaloo@gmail.com'),
    ('Jérémy MARC', 'jeremy.marc@gmail.com'),
)

MANAGERS = ADMINS

APP_BRAND_NAME = os.environ.get('APP_BRAND_NAME', 'Cook&Be')

FROM_EMAIL_HOST = os.environ.get('FROM_EMAIL_HOST', 'localhost')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'root@localhost')

# https://dev.to/weplayinternet/upgrading-to-django-3-2-and-fixing-defaultautofield-warnings-518n
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# PATHS

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
DJANGO_PATH = os.path.abspath(os.path.join(PROJECT_PATH, ".."))

if TESTING:
    APP_BASE_URL = 'https://app.localhost'
    CMS_BASE_URL = 'https://www.localhost'

    from smart_testing.cursors import TracebackCursorWrapper
    from django.db.backends import utils as db_utils

    db_utils.CursorDebugWrapper = TracebackCursorWrapper
    TEST_RUNNER = "smart_testing.runners.SmartDiscoverRunner"
    SMART_TESTING = {
        "SUCCESS_ASCII_FILEPATH": "/django-static/smart-testing-success.txt",
        "POSTGRESQL_EXTENSIONS": ["unaccent"],
        "CAPTURE_PRINTS": True,
    }

else:
    APP_BASE_URL = os.environ.get('APP_BASE_URL', 'undefined')
    CMS_BASE_URL = os.environ.get('CMS_BASE_URL', 'undefined')


SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'support@cookandbe.com')
ENABLE_AUTO_BCC = os.environ.get('ENABLE_AUTO_BCC', 'False') == 'True'

OP_ENABLE_PUBLIC_PAYMENT = os.environ.get('OP_ENABLE_PUBLIC_PAYMENT', 'True') == 'True'

# base URL for sitemap
SITE_BASE_URL = CMS_BASE_URL

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', 'dev_sendgrid_key')

# Session expiration time (8 weeks)
SESSION_COOKIE_AGE = 4838400

DATABASES = {}


def set_pgsql_db():
    """
    Configure Optalim with a PGSQL database (production)
    """
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'undefined'),
        'USER': os.environ.get('DB_USERNAME', 'undefined'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'undefined'),
        'HOST': os.environ.get('DB_HOSTNAME', 'undefined'),
        'PORT': os.environ.get('DB_PORT', 'undefined')
    }

def set_sqlite_db():
    """
    Configure Optalim with an in-memory SQLITE database (tests only)
    """
    print("*** Testing using a SQLite database. Use ./manage.py test_prod to use PGSQL ***", file=sys.stderr)
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory',
    }


# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = json.loads(os.environ.get('ALLOWED_HOSTS', '["*"]'))

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-FR'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = '/django-static'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Storage for static files
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'undefined')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'undefined')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'undefined')

AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_REGION_NAME = "eu-west-1"


if TESTING:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_ROOT = '/'
    APP_BASE_URL = 'https://app.localhost'
    CMS_BASE_URL = 'https://www.localhost'

    from smart_testing.cursors import TracebackCursorWrapper
    from django.db.backends import utils as db_utils

    db_utils.CursorDebugWrapper = TracebackCursorWrapper
    TEST_RUNNER = "smart_testing.runners.SmartDiscoverRunner"
    SMART_TESTING = {
        "SUCCESS_ASCII_FILEPATH": f"{STATIC_ROOT}/smart-testing-success.txt",
        "POSTGRESQL_EXTENSIONS": ["unaccent"],
        "CAPTURE_PRINTS": True,
    }

else:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    APP_BASE_URL = os.environ.get('APP_BASE_URL', 'undefined')
    CMS_BASE_URL = os.environ.get('CMS_BASE_URL', 'undefined')

ANGULAR_APP_BASE_URL = os.environ.get('ANGULAR_APP_BASE_URL')

# Mongo
MONGO_HOST = os.environ.get('MONGO_HOST', 'undefined'),
MONGO_PORT = 27017

FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID', '1561887264033548')
FACEBOOK_SECRET_KEY = os.environ.get('FACEBOOK_SECRET_KEY', '24e3b5b8568b48aef30405ed17264817')

FACEBOOK_APP_ACCESS_TOKEN = FACEBOOK_APP_ID + '|' + FACEBOOK_SECRET_KEY
FACEBOOK_API_VERSION = "3.0"

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0cv+!@y^&a(a(5cww6$jnhq@yy3_qb*p%xh*2jchc6wsm!yf@a'

MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'middleware.log_exceptions.ExceptionMiddleware',
    'middleware.disable_csrf.DisableCSRF',
    'qinspect.middleware.QueryInspectMiddleware',
    'optalim.error_handler.BodySaveMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

if DEBUG_TOOLBAR_ENABLED:
    # Enabling debug toolbar
    MIDDLEWARE = ('debug_panel.middleware.DebugPanelMiddleware',) + MIDDLEWARE


ROOT_URLCONF = 'optalim.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'optalim.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            DJANGO_PATH
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


SYSTEM_APPS = [
        'django.contrib.admin',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.postgres',
        'rest_framework',
        'django_extensions',
        'corsheaders',
        'ext_tests',
        'storages',
    ]

CUSTOM_APPS = [
        'planning_mgr',
        'storage_mgr',
        'shopping_mgr',
        'eater_mgr',
        'profile_mgr',
        'recipe_mgr',
        'discussion',
        'user_mgr',
        'location_mgr',
        'provider_mgr',
        'diet_mgr',
        'notify_mgr',
        'polls',
        'newsletters',
        'emailing',
        'articles',
        'nutrient',
        'paybox',
        'blogs',
        'abtest',
        'seo',
        'secure',
        'hippocrate',
        'common'
    ]

INSTALLED_APPS = SYSTEM_APPS + CUSTOM_APPS

# In test, disable migrations
if TESTING:
    class DisableMigrations(object):

        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return None

    MIGRATION_MODULES = DisableMigrations()

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

AUTH_USER_MODEL = "user_mgr.User"

if TESTING:
    CACHES = {
        'default': {
            'BACKEND': 'common.dummy.DummyCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_SERVER', 'redis:6379'),
            "OPTIONS": {
                "SOCKET_CONNECT_TIMEOUT": 5,  # seconds
                "SOCKET_TIMEOUT": 5,  # seconds
                "CONNECTION_POOL_KWARGS": {"max_connections": 100, "retry_on_timeout": True}
            }
        }
    }

    ### DISABLED 01/06/15 : to make sessions more persistend, store them in PGSQL
    # Let Django use Redis to store the sessions
    # SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    # SESSION_CACHE_ALIAS = 'default'

# Configuration of Celery : where will be stored results of asynchronous calls
# Uncomment for debugging purposes only, or if you want to retrieve results from asynchronous calculation
#CELERY_RESULT_BACKEND = 'mongodb://127.0.0.1:27017/'
#CELERY_MONGODB_BACKEND_SETTINGS = {
#    'database': 'celery',
#    'taskmeta_collection': 'results',
#}

CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_IGNORE_RESULT = True  # Don't store results of async calls
CELERY_BROKER_URL = os.environ.get("RABBITMQ_URL", None)

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
   'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
       #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
   ],
       'DEFAULT_AUTHENTICATION_CLASSES': (
           'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'UPLOADED_FILES_USE_URL': True
}

if not DEBUG:
    # No debugging renderer
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ['rest_framework.renderers.JSONRenderer']

AUTHENTICATION_BACKENDS = (
    'user_mgr.auth.PublicAuthBackend',
    'user_mgr.auth.ProAuthBackend'
)

####  The following lines need to be uncommented (with the corsheaders middleware too)
####  if backend and frontend are put on different servers
# CORS_ALLOWED_ORIGINS = [
#     "http://app.cookandbe.localhost",
#     "app.cookandbe.localhost"
# ]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_HEADERS = (
    *default_headers,
    "Sentry-Trace",
)

# If True, recipes are loaded in memory when the server starts
# This is required to enable planning generation
PRELOAD_RECIPES = True

# To prevent encoding errors
FILE_CHARSET = "utf-8"

# Paybox configuration
E_TRANSACTION_PUBLIC_KEY_PATH = os.path.join(PROJECT_PATH, 'paybox_public.pem')
PBX_SITE = os.environ.get('PBX_SITE', '')  # Our paybox site (given by Paybox)
PBX_RANG = os.environ.get('PBX_RANG', '')  # Our paybox rank (given by Paybox)
PBX_IDENTIFIANT = os.environ.get('PBX_IDENTIFIANT', '') # E-transaction identifier (given by e-transaction)
PBX_HMAC_KEY = os.environ.get('PBX_HMAC_KEY', '')
PBX_URL = os.environ.get('PBX_URL', '')


ENABLE_PUBLIC_PAYMENT = os.environ.get('ENABLE_PUBLIC_PAYMENT', 'True') == 'True'

ENABLE_EMAILS = os.environ.get('ENABLE_EMAILS', 'True') == 'True'
EMAIL_MODE = os.environ.get('EMAIL_MODE', 'log')

ENABLE_MEALS_SUGGESTION = os.environ.get('ENABLE_MEALS_SUGGESTION', 'True') == 'True'
ENABLE_PLANNING_REMINDER = os.environ.get('ENABLE_PLANNING_REMINDER', 'True') == 'True'
ENABLE_MEALS_REMINDER = os.environ.get('ENABLE_MEALS_REMINDER', 'True') == 'True'

DEFAULT_EMAIL_DAILY = os.environ.get('DEFAULT_EMAIL_DAILY', 'True') == 'True'
DEFAULT_EMAIL_SUGGESTION = os.environ.get('DEFAULT_EMAIL_SUGGESTION', 'True') == 'True'
DEFAULT_EMAIL_NEWSLETTER = os.environ.get('DEFAULT_EMAIL_NEWSLETTER', 'True') == 'True'

# if not TESTING or TESTING_WITH_PGSQL:
set_pgsql_db()
# else:
#     set_sqlite_db()



QUERY_INSPECT_ENABLED = os.environ.get('QUERY_INSPECT_ENABLED', 'False') == 'True'  # Turn to true to get enormous debug informations about SQL queries !
QUERY_INSPECT_LOG_STATS = True
QUERY_INSPECT_LOG_QUERIES = True
QUERY_INSPECT_LOG_TRACEBACKS = True
QUERY_INSPECT_TRACEBACK_ROOTS = [DJANGO_PATH]

def before_send(event, hint):
    if "logentry" in event:
        message = event["logentry"].get("message")
        if "HTTP 404" in message and ".php" in message:
            print("Skip some bot attempt to reach PHP pages")
            return None
    return event

# Sentry configuration (https://docs.sentry.io/platforms/python/configuration/options/)
SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
if SENTRY_DSN:
    # https://docs.sentry.io/platforms/python/django/
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.WARNING,  # Send warnings and errors as events
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), RedisIntegration(), sentry_logging],
        release=f"{FROM_EMAIL_HOST}@{ENVIRONMENT}",
        environment=ENVIRONMENT,

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=0.01,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=False,

        before_send=before_send
    )
    print("SENTRY ENABLED")
