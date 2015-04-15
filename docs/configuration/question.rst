Question Configuration
======================

Contains the configuration of a question.

The configuration of a Question is only part of the
:doc:`/configuration/questionnaire`.

.. seealso::
    :class:`configuration.configuration.QuestionnaireQuestion`

+-----------------+----------------------------------------------------+
| Parent element: | :doc:`/configuration/questiongroup`                |
+-----------------+----------------------------------------------------+
| Child element:  | :doc:`/configuration/key`                          |
+-----------------+----------------------------------------------------+


Format
------

The basic format of the configuration is as follows::

  {
    # The keyword of the key of the question.
    "keyword": "KEY",

    # (optional)
    "in_list": true,

    # (optional)
    "form_template": "TEMPLATE_NAME",

    # (optional)
    "conditional": true,

    # (optional)
    "conditions": [],

    # (optional)
    "questiongroup_conditions": [],

    # (optional)
    "max_length": 500,

    # (optional)
    "num_rows": 10
  }

.. seealso::
    For more information on the configuration of its child elements,
    please refer to their respective documentation:

    * :doc:`/configuration/key`
    * :doc:`/configuration/value`

    Also refer to the :ref:`configuration_questionnaire_example` of a
    Questionnaire configuration.


``keyword``
^^^^^^^^^^^

The keyword of the key of this question.

``in_list``
^^^^^^^^^^^

(Optional). An optional boolean indicating whether this question should
appear in the list representation of questionnaires or not. Defaults to
``False``, meaning that this question is not shown in the list.

``form_template``
^^^^^^^^^^^^^^^^^

(Optional). An optional name of a template to be used for the rendering
of the question form. The name of the template needs to match a file
with the ending ``.html`` inside
``questionnaire/templates/form/question/``. If not specified, the
default layout for each key type is used (usually ``default.html``).

The following question templates exist. Please note that not every
template should be used with any field type.

+--------------------+--------------------------------------------------------+
| ``default``        | Label on top, field below it.                          |
|                    |                                                        |
|                    | The default for most key types.                        |
+--------------------+--------------------------------------------------------+
| ``inline_2``       | Label on the left (aligned right in a 2 column div),   |
|                    | field on the right (in a 10 column div).               |
+--------------------+--------------------------------------------------------+
| ``inline_3``       | Label on the left (in a 3 column div), field on the    |
|                    | right (in a 9 column div).                             |
|                    |                                                        |
|                    | The default for key type ``measure``.                  |
+--------------------+--------------------------------------------------------+
| ``no_label``       | No label (should be handled by the field).             |
|                    |                                                        |
|                    | The default for key type ``image_checkbox``            |
+--------------------+--------------------------------------------------------+

``conditional``
^^^^^^^^^^^^^^^

(Optional). An optional boolean indicating whether this question is only
shown depending on the condition (value) of another question. If set to
``true``, another question of this questiongroup should have the option
``conditions`` set.

.. important::
    Questions with ``"conditional": true`` need to be listed **before**
    the question with ``"conditions": []`` triggering them.

``conditions``
^^^^^^^^^^^^^^

(Optional). An optional list of conditions triggering conditional
questions. Each condition must have the format
``""value_keyword|Boolean|key_keyword""``. Example::

    "conditions": ["value_15_1|True|key_16"]

For the time being, conditions can only be set for Key
(see :doc:`/configuration/key`) with type ``image_checkbox``.

``questiongroup_conditions``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(Optional). An optional list of conditions triggering conditional
questiongroups. Each condition must have the format
``"expresssion|condition_name"`` where ``expression`` is part of a valid
(Python and Javascript!) boolean expression and ``condition_name`` is
the name of a Questiongroup's ``questiongroup_condition`` option.

Example::

    "questiongroup_conditions": [">1|questiongroup_17", "<3|questiongroup_17"]

.. seealso::
    :doc:`/configuration/questiongroup`

``max_length``
^^^^^^^^^^^^^^

(Optional). An optional integer to specify the maximum length of
characters for this value. Renders as a validator for text fields. This
is only meaningful for key types ``char`` (default value: 200) and
``text`` (default value: 500).

``num_rows``
^^^^^^^^^^^^

(Optional). An optional integer to define the number of rows to be shown
for textarea fields. This is only meaningful for key type ``text``.
Defaults to 10.
