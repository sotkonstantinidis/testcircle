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
    "view_template": "VIEW_TEMPLATE",

    # (optional)
    "include_toc": true,

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


``view_template``
^^^^^^^^^^^^^^^^^

(Optional). An optional name of a template to be used for the rendering
of the section details. The name of the template needs to match a file
with the ending ``.html`` inside
``questionnaire/templates/details/section/``. If not specified, the
default layout (``default.html``) for the section is used.


``include_toc``
^^^^^^^^^^^^^^^

(Optional). An optional boolean indicating whether to add a table of
contents to the current section or not. The ToC is rendered at the top
of the section. Defaults to ``False``.


``categories``
^^^^^^^^^^^^^^

A list of :doc:`/configuration/category`.
