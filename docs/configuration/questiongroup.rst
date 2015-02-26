Questiongroup Configuration
===========================

Contains the configuration of a questiongroup.

The configuration of a Questiongroup is stored in a JSON format in the
``configuration`` field of :class:`configuration.models.Questiongroup`.
It can also be overwritten in the :doc:`/configuration/questionnaire`.

.. seealso::
    :class:`configuration.configuration.QuestionnaireQuestiongroup`

+-----------------+----------------------------------------------------+
| Parent element: | :doc:`/configuration/subcategory`                  |
+-----------------+----------------------------------------------------+
| Child element:  | :doc:`/configuration/question`                     |
+-----------------+----------------------------------------------------+


Format
------

The basic format of the configuration is as follows::

  {
    # The keyword of the questiongroup.
    "keyword": "QUESTIONGROUP_KEYWORD",

    # (optional)
    "template": "TEMPLATE_NAME",

    # (optional)
    "min_num": 1,

    # (optional)
    "max_num": 1,

    # A list of questions.
    "questions": [
      # ...
    ]
  }

.. seealso::
    For more information on the configuration of its child elements,
    please refer to their respective documentation:

    * :doc:`/configuration/question`

    Also refer to the :ref:`configuration_questionnaire_example` of a
    Questionnaire configuration.


``keyword``
^^^^^^^^^^^

The keyword of the questiongroup.

.. hint::
    Each keyword of a questiongroup needs to be unique throughout all
    questionnaires. This is because questionnaire data is stored by
    their questiongroup keyword and when queried it needs to be mapped
    to the correct questiongroup.

``template``
^^^^^^^^^^^^

(Optional). An optional name of a template to be used for the rendering
of the questions within the questiongroup. The name of the template
needs to match a file inside
``questionnaire/templates/form/questiongroup``. If not specified, the
default layout (``default.html``) is used.

The following questiongroup templates exist. Please note that some of
them should only be used in combination with certain keys.

+--------------------+--------------------------------------------------------+
| ``default``        | Renders each field with a simple label on top.         |
+--------------------+--------------------------------------------------------+
| ``inline_1``       | Renders each field with the label in front of it, for  |
|                    | example for short text fields.                         |
+--------------------+--------------------------------------------------------+
| ``measure``        | Renders a measure field with the label in front of it. |
+--------------------+--------------------------------------------------------+

``min_num``
^^^^^^^^^^^

(Optional). The minimum for repeating questiongroups to appear. Defaults
to 1.

``max_num``
^^^^^^^^^^^

(Optional). The maximum for repeating questiongroups to appear. If
larger than ``min_num``, buttons to add or remove questiongroups will be
rendered in the form. Defaults to ``min_num``.

``questions``
^^^^^^^^^^^^^

A list of :doc:`/configuration/question`.
