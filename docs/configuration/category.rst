Category Configuration
======================

Contains the configuration of a category.

The configuration of a Category is only part of the
:doc:`/configuration/questionnaire`.

.. seealso::
    :class:`configuration.configuration.QuestionnaireCategory`

+-----------------+----------------------------------------------------+
| Parent element: | :doc:`/configuration/questionnaire`                |
+-----------------+----------------------------------------------------+
| Child element:  | :doc:`/configuration/subcategory`                  |
+-----------------+----------------------------------------------------+


Format
------

The basic format of the configuration is as follows::

  {
    # The keyword of the category.
    "keyword": "CAT_KEYWORD",

    # (optional)
    "view_template": "VIEW_TEMPLATE",

    # (optional)
    "use_raw_data": true,

    # A list of subcategories.
    "subcategories": [
      {
        # ...
      }
    ]
  }

.. seealso::
    For more information on the configuration of its child elements,
    please refer to their respective documentation:

    * :doc:`/configuration/subcategory`

    Also refer to the :ref:`configuration_questionnaire_example` of a
    Questionnaire configuration.


``keyword``
^^^^^^^^^^^

The keyword of the category.


``view_template``
^^^^^^^^^^^^^^^^^

(Optional). An optional name of a template to be used for the rendering
of the category details. The name of the template needs to match a file
with the ending ``.html`` inside
``questionnaire/templates/details/category/``. If not specified, the
default layout (``default.html``) for the category is used.


``use_raw_data``
^^^^^^^^^^^^^^^^

(Optional). An optional boolean indicating whether to add the raw
category data to the template or not. These values can then be used for
example for manual rendering of the category details. Defaults to
``False``.

.. seealso::
  :func:`configuration.configuration.QuestionnaireCategory.get_raw_category_data`


``subcategories``
^^^^^^^^^^^^^^^^^

A list of :doc:`/configuration/subcategory`.
