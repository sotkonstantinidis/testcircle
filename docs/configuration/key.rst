Key Configuration
=================

The configuration of a Key is stored in a JSON format in the ``data``
field of :class:`configuration.models.Key`.

Format
------

The basic format of the configuration is as follows::

  {
    "type": "TYPE"
  }

``type``
^^^^^^^^

The following options are valid for ``type``. Default type is ``char``.

+--------------------+--------------------------------------------------------+
| ``char``           | A simple textfield for short text, with the label      |
|                    | above the field.                                       |
+--------------------+--------------------------------------------------------+
| ``shortchar``      | A textfield for very short text with the label next to |
|                    | the field.                                             |
+--------------------+--------------------------------------------------------+
| ``text``           | A textarea for larger text                             |
+--------------------+--------------------------------------------------------+
