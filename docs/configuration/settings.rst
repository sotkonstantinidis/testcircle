Application settings
====================

This chapter covers the configuration of the QCAT application. The pattern
```config``` from the 12 factor app is widely followed, so many variables are
stored in the environment.

For easy management of environment variables, the package `envdir`_ is used.
The variables are stored in the folder ```/envs```; your folder should look as
follows ::

    envs/
    ├── AUTH_API_KEY
    ├── AUTH_API_URL
    ├── CACHE_URL
    ├── DATABASE_URL
    ├── DJANGO_ALLOWED_HOSTS
    ├── DJANGO_CONFIGURATION
    ├── DJANGO_DEBUG
    ├── DJANGO_SECRET_KEY
    ├── DJANGO_SETTINGS_MODULE
    ├── DJANGO_TEMPLATE_DEBUG
    ├── DJANGO_USE_CACHING
    ├── MAINTENANCE_MODE
    └── TESTING_FIREFOX_PATH


.. seealso::
    `dj-database-url`_ for the format of ```DATABASE_URL```
.. seealso::
    `django-cache-url`_ for the format of ```CACHE_URL```

.. _envdir: https://pypi.python.org/pypi/envdir
.. _dj-database-url: https://github.com/kennethreitz/dj-database-url
.. _django-cache-url: https://github.com/ghickman/django-cache-url


Django settings
---------------

Most of the settings are identical to the Django settings. Please refer
to the `Django documentation`_ for further information.

.. _Django documentation: https://docs.djangoproject.com/en/1.8/ref/settings/

Following environment variables must be set in order for django to run:

    * ``DJANGO_CONFIGURATION``
    * ``DJANGO_SECRET_KEY``
    * ``DJANGO_SETTINGS_MODULE``
    * ``DATABASE_URL``

``DJANGO_ALLOWED_HOSTS``
^^^^^^^^^^^^^^^^^^^^^^^^
Default: ``'localhost', '127.0.0.1'``

``DJANGO_CONFIGURATION``
^^^^^^^^^^^^^^^^^^^^^^^^
For development: ``DevDefaultSite``

``DJANGO_DEBUG``
^^^^^^^^^^^^^^^^
Default: ``False``

``DJANGO_SECRET_KEY``
^^^^^^^^^^^^^^^^^^^^^
Default: ``None``

``DJANGO_SETTINGS_MODULE``
^^^^^^^^^^^^^^^^^^^^^^^^^^
For development: ``apps.qcat.settings``

``DJANGO_TEMPLATE_DEBUG``
^^^^^^^^^^^^^^^^^^^^^^^^^
Default: ``False``

``DJANGO_USE_CACHING``
^^^^^^^^^^^^^^^^^^^^^^
Default: ``True``


QCAT settings
-------------

All settings can be overwritten by an environment variable unless stated
otherwise.

``API_PAGE_SIZE``
^^^^^^^^^^^^^^^^^
Page size of results for the API providing questionnaire details.

Default: ``25``

``AUTH_API_KEY``
^^^^^^^^^^^^^^^^
Default: ``None``

``AUTH_API_TOKEN``
^^^^^^^^^^^^^^^^^^
The API token used for the authentication.

Default: ``None``

``AUTH_API_URL``
^^^^^^^^^^^^^^^^
Default: ``https://beta.wocat.net/api/v1/``

``AUTH_API_USER``
^^^^^^^^^^^^^^^^^
Default: ``None``

``AUTH_COOKIE_NAME``
^^^^^^^^^^^^^^^^^^^^
Default: ``fe_typo_user``

``AUTH_LOGIN_FORM``
^^^^^^^^^^^^^^^^^^^
Default: ``https://dev.wocat.net/en/sitefunctions/login.html``

``BASE_URL``
^^^^^^^^^^^^
Default: ``https://qcat.wocat.net``

``CACHE_URL``
^^^^^^^^^^^^^

``DATABASE_URL``
^^^^^^^^^^^^^^^^
Default: ``None``

.. seealso::
    `dj-database-url`_ for the format of ```DATABASE_URL```

``DEPLOY_TIMEOUT``
^^^^^^^^^^^^^^^^^^
Timeout between announcement of deploy and actual maintenance window in seconds.

Default: ``900``

``DO_SEND_EMAILS``
^^^^^^^^^^^^^^^^^^
Default: ``False``

``DO_SEND_STAFF_ONLY``
^^^^^^^^^^^^^^^^^^^^^^
Default: ``True``

``ES_HOST``
^^^^^^^^^^^
Default: ``localhost``

``ES_INDEX_PREFIX``
^^^^^^^^^^^^^^^^^^^
Default: ``qcat_``

``ES_NESTED_FIELDS_LIMIT``
^^^^^^^^^^^^^^^^^^^^^^^^^^
Default: ``250``

``ES_PORT``
^^^^^^^^^^^
Default: ``9200``

``ES_QUERY_RESERVED_CHARS``
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Some charactes have special meaning to ES queries.
https://www.elastic.co/guide/en/elasticsearch/reference/2.0/query-dsl-query-string-query.html#_reserved_characters

.. hint::
    This setting cannot be overwritten by an environment variable.

Default: ``['\\', '+', '-', '=', '&&', '||', '>', '<', '!', '(', ')', '{', '}', '[', ']', '^', '"', '~', '*', '?', ':', '/']``

``GOOGLE_MAPS_JAVASCRIPT_API_KEY``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``None``

``GOOGLE_WEBMASTER_TOOLS_KEY``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``None``

``HOST_STRING_DEMO``
^^^^^^^^^^^^^^^^^^^^
Used for continuous delivery (fabric).

Default: ``None``

``HOST_STRING_DEV``
^^^^^^^^^^^^^^^^^^^
Used for continuous delivery (fabric).

Default: ``None``

``HOST_STRING_LIVE``
^^^^^^^^^^^^^^^^^^^^
Used for continuous delivery (fabric).

Default: ``None``

``IS_ACTIVE_FEATURE_MODULE``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Feature toggle for questionnaire-modules

Default: ``False``

``IS_ACTIVE_FEATURE_WATERSHED``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Feature toggle for questionnaire 'watershed'

Default: ``False``

``KEY_PREFIX``
^^^^^^^^^^^^^^

Default: ``''``

``MAINTENANCE_LOCKFILE_PATH``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. hint::
    This setting cannot be overwritten by an environment variable.

``MAINTENANCE_MODE``
^^^^^^^^^^^^^^^^^^^^
See https://github.com/shanx/django-maintenancemode

Default: ``False``

``NEXT_MAINTENANCE``
^^^^^^^^^^^^^^^^^^^^
See https://github.com/shanx/django-maintenancemode

.. hint::
    This setting cannot be overwritten by an environment variable.

``OPBEAT``ls
^^^^^^^^^^
Opbeat configuration as dictionary.

Default: ``None``

``PIWIK_API_VERSION``
^^^^^^^^^^^^^^^^^^^^^
Default: ``1``

``PIWIK_AUTH_TOKEN``
^^^^^^^^^^^^^^^^^^^^
Default: ``None``

``PIWIK_SITE_ID``
^^^^^^^^^^^^^^^^^
Default: ``None``

``PIWIK_URL``
^^^^^^^^^^^^^
Default: ``https://piwik.wocat.net/``

``REACTIVATE_WOCAT_ACCOUNT_URL``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An URL to which users are redirected if the login failed because their account
is not yet activated. Background is that upon switching to the new WOCAT website
in 2017, all existing user accounts have to be reactivated manually.

Default: ``https://beta.wocat.net/accounts/reactivate/``

``REST_FRAMEWORK``
^^^^^^^^^^^^^^^^^^
Settings for: ``http://www.django-rest-framework.org/``

.. hint::
    This setting cannot be overwritten by an environment variable.

``SEND_MAILS``
^^^^^^^^^^^^^^

``SUMMARY_PDF_PATH``
^^^^^^^^^^^^^^^^^^^^
Path to folder to store/'cache' created pdfs

.. hint::
    This setting cannot be overwritten by an environment variable.

``SWAGGER_SETTINGS``
^^^^^^^^^^^^^^^^^^^^
See https://django-rest-swagger.readthedocs.io/en/latest/

.. hint::
    This setting cannot be overwritten by an environment variable.

``TEMP_UNCCD_TEST``
^^^^^^^^^^^^^^^^^^^
A temporary list of email addresses (users) which are part of UNCCD flagging
group.

Default: ``None``

``TESTING_FIREFOX_PATH``
^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``None``

``THUMBNAIL_ALIASES``
^^^^^^^^^^^^^^^^^^^^^

.. hint::
    This setting cannot be overwritten by an environment variable.

``TOUCH_FILE_DEMO``
^^^^^^^^^^^^^^^^^^^
Location of uwsgi-touchfile, used for continuous delivery.

Default: ``None``

``TOUCH_FILE_DEV``
^^^^^^^^^^^^^^^^^^
Location of uwsgi-touchfile, used for continuous delivery.

Default: ``None``

``TOUCH_FILE_LIVE``
^^^^^^^^^^^^^^^^^^^
Location of uwsgi-touchfile, used for continuous delivery.

Default: ``None``

``UPLOAD_IMAGE_THUMBNAIL_FORMATS``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A dictionary specifying the different thumbnail formats for images. For
every uploaded image, a thumbnail is created in each of the formats.

Example::

    UPLOAD_IMAGE_THUMBNAIL_FORMATS = {

        # '[NAME]': ([WIDTH], [HEIGHT])
        'header': (900, 300),

        'small': (200, 100),
    }

.. hint::
    This setting cannot be overwritten by an environment variable.

``UPLOAD_MAX_FILE_SIZE``
^^^^^^^^^^^^^^^^^^^^^^^^
An integer indicating the maximum file size for a single file upload.
In Bytes.

.. hint::
    This setting cannot be overwritten by an environment variable.

``UPLOAD_VALID_FILES``
^^^^^^^^^^^^^^^^^^^^^^
A dictionary indicating what file types are valid for upload and with
which extension they shall be saved.

Example::

    UPLOAD_VALID_FILES = {

        # 'TYPE': Used to group different types of files
        'image': (

            # ('[CONTENT_TYPE]', 'FILE_EXTENSION')
            ('image/jpeg', 'jpg'),
            ('image/png', 'png'),
            ('image/gif', 'gif'),
        ),
        'document': (
            ('application/pdf', 'pdf'),
        )
    }

.. hint::
    This setting cannot be overwritten by an environment variable.

``USE_NEW_WOCAT_AUTHENTICATION``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A boolean indicating whether to use the new (2017) WOCAT website as
authentication service or not.

Default: ``False``

``WARN_HEADER``
^^^^^^^^^^^^^^^
Text to display as warn header at the bottom of the page.

Default: ``None``

``WOCAT_IMPORT_DATABASE_URL``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
URL that was initially used to import existing WOCAT cases from QA and QT.

Default: ``None``

``WORD_WRAP_LANGUAGES``
^^^^^^^^^^^^^^^^^^^^^^^
List of languages to add the css-attribute: word-wrap. Use this with languages
without spaces between words, such as Khmer.

.. hint::
    This setting cannot be overwritten by an environment variable.
