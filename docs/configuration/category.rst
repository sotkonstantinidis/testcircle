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

``subcategories``
^^^^^^^^^^^^^^^^^

A list of :doc:`/configuration/subcategory`.
