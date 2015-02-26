Subcategory Configuration
=========================

Contains the configuration of a subcategory.

The configuration of a Subcategory is only part of the
:doc:`/configuration/questionnaire`.

.. seealso::
    :class:`configuration.configuration.QuestionnaireSubcategory`

+-----------------+----------------------------------------------------+
| Parent element: | :doc:`/configuration/category`                     |
+-----------------+----------------------------------------------------+
| Child element:  | :doc:`/configuration/questiongroup`                |
+-----------------+----------------------------------------------------+


Format
------

The basic format of the configuration is as follows::

  {
    # The keyword of the subcategory.
    "keyword": "SUBCAT_KEYWORD",

    # A list of questiongroups.
    "questiongroups": [
      # ...
    ]
  }

.. seealso::
    For more information on the configuration of its child elements,
    please refer to their respective documentation:

    * :doc:`/configuration/questiongroup`

    Also refer to the :ref:`configuration_questionnaire_example` of a
    Questionnaire configuration.


``keyword``
^^^^^^^^^^^

The keyword of the category.

``questiongroups``
^^^^^^^^^^^^^^^^^^

A list of :doc:`/configuration/questiongroup`.
