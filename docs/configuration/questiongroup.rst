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
    "min_num": 1,

    # (optional)
    "max_num": 1,

    # (optional)
    "questiongroup_condition": "CONDITION_NAME",

    # (optional)
    "view_template": "VIEW_TEMPLATE",

    # (optional)
    "numbered": "NUMBERED",

    # (optional)
    "detail_level": "DETAIL_LEVEL",

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

``min_num``
^^^^^^^^^^^

(Optional). The minimum for repeating questiongroups to appear. Defaults
to 1.

``max_num``
^^^^^^^^^^^

(Optional). The maximum for repeating questiongroups to appear. If
larger than ``min_num``, buttons to add or remove questiongroups will be
rendered in the form. Defaults to ``min_num``.

``questiongroup_condition``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

(Optional). An optional name of a condition valid for this
questiongroup. The name must correspond to one of
``questiongroup_conditions`` of a Question configuration.

.. seealso::
    :doc:`/configuration/question`

``view_template``
^^^^^^^^^^^^^^^^^

(Optional). An optional name of a template to be used for the rendering
of the questiongroup in the detail view. The name of the template needs
to match a file with the ending ``.html`` inside
``questionnaire/templates/details/questiongroup/``. If not specified,
the default layout (``default.html``) is used.

The following question templates exist. Please note that not every
template should be used with any field type.

+-------------------------+---------------------------------------------------+
| ``default``             | Simply renders each question of the questiongroup |
|                         | without additional output.                        |
|                         |                                                   |
|                         | This is the default.                              |
+-------------------------+---------------------------------------------------+
| ``bars``                | Renders all questions of the questiongroup as     |
|                         | horizontal bars.                                  |
|                         |                                                   |
|                         | Should only be used for questiongroups containing |
|                         | only questions with type ``measure``.             |
+-------------------------+---------------------------------------------------+
| ``bars_pyramid``        | Renders all questions of the questiongroup as     |
|                         | horizontal bars in the form of a pyramid (steps   |
|                         | ascending on the right side).                     |
|                         |                                                   |
|                         | Should only be used for questiongroups containing |
|                         | only questions with type ``measure``.             |
+-------------------------+---------------------------------------------------+
| ``bars_pyramid_center`` | Renders all questions of the questiongroup as     |
|                         | horizontal bars in the form of a pyramid (steps   |
|                         | ascending on either side).                        |
|                         |                                                   |
|                         | Should only be used for questiongroups containing |
|                         | only questions with type ``measure``.             |
+-------------------------+---------------------------------------------------+
| ``bars_pyramid_desc``   | Renders all questions of the questiongroup as     |
|                         | horizontal bars in the form of a pyramid (steps   |
|                         | descending the left side).                        |
|                         |                                                   |
|                         | Should only be used for questiongroups containing |
|                         | only questions with type ``measure``.             |
+-------------------------+---------------------------------------------------+

``numbered``
^^^^^^^^^^^^

(Optional). An optional parameter if the questiongroup is to be
numbered. Possible values are ``inline`` (numbering inside field label)
or ``prefix`` (numbering indented before fields). If not specified, no
numbering is used.

.. hint::
    If possible, ``prefix`` should be used.

``detail_level``
^^^^^^^^^^^^^^^^

(Optional). An optional parameter if the questiongroup contains
additional, mostly more detailed questions which are only visible after
clicking on a link. This is used for the "Plus"-Questions. The value of
the parameter can be freely chosen.

``questions``
^^^^^^^^^^^^^

A list of :doc:`/configuration/question`.
