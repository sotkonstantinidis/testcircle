Application settings
====================

This chapter covers the configuration of the QCAT application. Most of
the settings are specified in ``qcat/settings.py``. Further settings can
be specified in ``qcat/settings_local.py``, where for example the
database passwords are stored.

.. important::
    Do not modify ``qcat/settings.py``! If you want do adjust
    some of the settings, use ``qcat/settings_local.py`` which will
    overwrite existing settings in ``qcat/settings.py``.


Django settings
---------------

Most of the settings are identical to the Django settings. Please refer
to the `Django documentation`_ for further information.

.. _Django documentation: https://docs.djangoproject.com/en/1.7/ref/settings/


QCAT settings
-------------

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


``UPLOAD_MAX_FILE_SIZE``
^^^^^^^^^^^^^^^^^^^^^^^^

An integer indicating the maximum file size for a single file upload.
In Bytes.


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
