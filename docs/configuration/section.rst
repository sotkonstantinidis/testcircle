Section Configuration
=====================

Contains the configuration of a section.

The configuration of a Section is only part of the
:doc:`/configuration/questionnaire`.

.. seealso::
    :class:`configuration.configuration.QuestionnaireSection`

+-----------------+----------------------------------------------------+
| Parent element: | :doc:`/configuration/questionnaire`                |
+-----------------+----------------------------------------------------+
| Child element:  | :doc:`/configuration/category`                     |
+-----------------+----------------------------------------------------+


Format
------

The basic format of the configuration is as follows::

  {
    # The keyword of the section.
    "keyword": "SECTION_KEYWORD",

    # (optional)
    "view_options": {},

    # (optional)
    "include_toc": true,

    # (optional)
    "review_panel": true,

    # A list of categories.
    "categories": [
      {
        # ...
      }
    ]
  }

.. seealso::
    For more information on the configuration of its child elements,
    please refer to their respective documentation:

    * :doc:`/configuration/category`

    Also refer to the :ref:`configuration_questionnaire_example` of a
    Questionnaire configuration.


``keyword``
^^^^^^^^^^^

The keyword of the section.


``view_options``
^^^^^^^^^^^^^^^^

(Optional). An optional object containing configuration options for the
view representation of the section.


``include_toc``
^^^^^^^^^^^^^^^

(Optional). An optional boolean indicating whether to add a table of
contents to the current section or not. The ToC is rendered at the top
of the section. Defaults to ``False``.


``review_panel``
^^^^^^^^^^^^^^^^

(Optional). An optional boolean indicating whether to include the review
panel at the top of the section or not. The review panel contains
actions related to the editing and moderation workflow (eg. submit,
publish).


``categories``
^^^^^^^^^^^^^^

A list of :doc:`/configuration/category`.
