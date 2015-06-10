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

    # (optional)
    "form_template": "TEMPLATE_NAME",

    # (optional)
    "view_template": "TEMPLATE_NAME",

    # (optional)
    "table_grouping": [],

    # A list of questiongroups.
    "questiongroups": [
      # ...
    ],

    # A list of subcategories.
    "subcategories": [
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

``form_template``
^^^^^^^^^^^^^^^^^

(Optional). An optional name of a template to be used for the rendering
of the subcategory form. The name of the template needs to match a file
with the ending ``.html`` inside
``questionnaire/templates/form/subcategory/``. If not specified, the
default layout (``default.html``) is used.

Please note that some templates require additional options to be set.

``view_template``
^^^^^^^^^^^^^^^^^

(Optional). An optional name of a template to be used for the rendering
of the subcategory form. The name of the template needs to match a file
with the ending ``.html`` inside
``questionnaire/templates/details/subcategory/``. If not specified, the
default layout (``default.html``) is used.

Please note that some templates require additional options to be set.

``table_grouping``
^^^^^^^^^^^^^^^^^^

(Optional). A nested array to define the layout of the table based on
the keywords of the questiongroups of the subcategory.

Example::

  "table_grouping": [
    ["qg_25", "qg_27"],
    ["qg_26", "qg_28"]
  ]

Creates the following table (with ``"view_template": "table_1"``):

+------------+------------+
| ``qg_25``  | ``qg_26``  |
+            +------------+
|            | ``qg_26``  |
+------------+------------+


``questiongroups``
^^^^^^^^^^^^^^^^^^

A list of :doc:`/configuration/questiongroup`.

.. important::
    The options ``questiongroups`` and ``subcategories`` are exclusive,
    they should not be set both at the same time.

``subcategories``
^^^^^^^^^^^^^^^^^

A list of :doc:`/configuration/subcategory`.

.. important::
    The options ``questiongroups`` and ``subcategories`` are exclusive,
    they should not be set both at the same time.
