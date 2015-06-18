"""
Django settings for qcat project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

"""
Many of the required settings must be defined in settings_local.py.
These are in particular:

* DATABASES
* DEBUG
* TEMPLATE_DEBUG
* ALLOWED_HOSTS
* SECRET_KEY
"""

# Application definition

INSTALLED_APPS = (
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_nose',
    'floppyforms',
    'django_extensions',
    'imagekit',
    'questionnaire',
    'accounts',
    'configuration',
    'wocat',
    'unccd',
    'search',
    'sample',
    'samplemulti',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'accounts.authentication.WocatAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'qcat.urls'

WSGI_APPLICATION = 'qcat.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, '../csr/locale'),
)

from django.utils.translation import ugettext_lazy as _
# The first language is the default language.
LANGUAGES = (
    ('en', _('English')),
    ('es', _('Spanish')),
)

TIME_ZONE = 'Europe/Zurich'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '..', 'static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

MEDIA_URL = '/upload/'
MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'upload')

UPLOAD_VALID_FILES = {
    'image': (
        ('image/jpeg', 'jpg'),
        ('image/png', 'png'),
        ('image/gif', 'gif'),
    ),
    'document': (
        ('application/pdf', 'pdf'),
    )
}
UPLOAD_MAX_FILE_SIZE = 1000000
UPLOAD_IMAGE_THUMBNAIL_FORMATS = (
    ('default', (640, 480)),
    ('small', (1024, 768)),
    ('medium', (1440, 1080)),
    # 'large' is the original uploaded image.
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request',
)

AUTH_USER_MODEL = 'accounts.User'
AUTHENTICATION_BACKENDS = (
    'accounts.authentication.WocatAuthenticationBackend',
)
LOGIN_URL = 'login'

# TODO: Try if tests can be run with --with-fixture-bundling
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--cover-html', '--cover-html-dir=coverage_html', '--cover-erase',
    '--cover-package=accounts,configuration,qcat,questionnaire,unccd',
    '--nologcapture']

GRAPPELLI_ADMIN_TITLE = 'QCAT Administration'
GRAPPELLI_INDEX_DASHBOARD = 'qcat.dashboard.CustomIndexDashboard'

# Elasticsearch settings
ES_HOST = 'localhost'
ES_PORT = 9200
ES_INDEX_PREFIX = 'qcat_'

# For each language (as set in the setting ``LANGUAGES``), a language
# analyzer can be specified. This helps to analyze the text in the
# corresponding language for better search results.
# https://www.elastic.co/guide/en/elasticsearch/reference/1.6/analysis-lang-analyzer.html
ES_ANALYZERS = (
    ('en', 'english'),
    ('es', 'spanish'),
)


try:
    from qcat.settings_local import *
except ImportError:
    pass
