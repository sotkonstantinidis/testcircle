Category Configuration
======================

Contains the configuration of a category.

The configuration of a Category is only part of the
:doc:`/configuration/questionnaire`.

.. seealso::
    :class:`configuration.configuration.QuestionnaireCategory`

+-----------------+----------------------------------------------------+
| Parent element: | :doc:`/configuration/section`                      |
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
    "view_options": {},

    # (optional)
    "use_raw_data": true,

    # (optional)
    "with_metadata": true,

    # (optional)
    "include_toc": true,

    # (optional)
    "additional_data": {},

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


``view_options``
^^^^^^^^^^^^^^^^

(Optional). An optional object containing configuration options for the
view representation of the category.


``use_raw_data``
^^^^^^^^^^^^^^^^

(Optional). An optional boolean indicating whether to add the raw
category data to the template or not. These values can then be used for
example for manual rendering of the category details. Defaults to
``False``.

.. seealso::
  :func:`configuration.configuration.QuestionnaireCategory.get_raw_category_data`


``with_metadata``
^^^^^^^^^^^^^^^^^

(Optional). An optional boolean indicating whether to add the metadata
of the current Questionnaire to the template or not. Defaults to ``False``.


``include_toc``
^^^^^^^^^^^^^^^

(Optional). An optional boolean indicating whether to add a table of
contents to the current category or not. The ToC is rendered at the top
of the category. Defaults to ``False``.


``additional_data``
^^^^^^^^^^^^^^^^^^^

(Optional). An optional object containing the keywords of questiongroups
and questions from which additional data is to be collected.

Example::

  {
    "qg_1": ["key_1"]
  }


``subcategories``
^^^^^^^^^^^^^^^^^

A list of :doc:`/configuration/subcategory`.
