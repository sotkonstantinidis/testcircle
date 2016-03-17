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
    "view_options": {
      # Default: "default"
      "template": "TEMPLATE_NAME",

      # Default: ""
      "label_position": "",

      # Default: "h5"
      "label_tag": "h5",

      # Default: ""
      "layout": "stacked",

      # Default: false
      "with_raw_values": true,

      # Default: false
      "in_list": true,

      # Default: false
      "is_name": true,

      # Default: false
      "filter": true
    },

    # (optional)
    "form_options": {
      # Default: "default"
      "template": "TEMPLATE_NAME",

      # Default: None
      "max_length": 500,

      # Default: 3
      "num_rows": 5,

      # Default: ""
      "helptext_position": "tooltip",

      # Default: ""
      "label_position": "placeholder",

      # Default: []
      "conditions": [],

      # Default: false
      "conditional": true,

      # Default: []
      "questiongroup_conditions": [],
    }
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


``view_options``
^^^^^^^^^^^^^^^^

(Optional). An optional object containing configuration options for the
view representation of the question.

  * ``template``: An optional template name. Must be a valid file name
    with ``.html`` ending in folder ``templates/details/question/``.

  * ``label_position`` (str): An optional indication for the label placement.
    Possible values are: ``none`` (no label displayed).

  * ``label_tag`` (str): Specifies the HTML tag used for the label (eg. ``h3``).
    By default, the tag ``<h5>`` is used.

  * ``layout`` (str): Additional indications used for the layout of the
    question. Known values are ``stacked`` for stacked measure bars.

  * ``with_raw_values`` (bool): Allows to also add the raw values (the keywords)
    to the list of values. This works for field types "checkbox", "cb_bool" and
    "radio". Defaults to ``false``.

  * ``in_list``: An optional boolean indicating whether this question
    should appear in the list representation of questionnaires or not.
    Defaults to ``False``, meaning that this question is not shown in
    the list.

  * ``is_name``: An optional boolean indicating whether this question
    represents the name of the entire Questionnaire.

    .. important::
        Only one question of the entire Questionnaire can have this
        flag. If the key is inside a repeating questiongroup, only the
        first appearance of the key will be used as name.

  * ``filter``: An optional boolean indicating whether this question is
    filterable or not. If set to ``True``, the question will appear in
    the filter dropdown.


``form_options``
^^^^^^^^^^^^^^^^

(Optional). An optional object containing configuration options for the
form representation of the question.

  * ``template``: An optional template name. Must be a valid file name
    with ``.html`` ending in folder ``templates/form/question/``.

  * ``max_length``: An optional integer to specify the maximum length of
    characters for this value. Renders as a validator for text fields.
    This is only meaningful for key types ``char`` (default value: 200)
    and ``text`` (default value: 500).

  * ``num_rows``: An optional integer to define the number of rows to be
    shown for textarea fields. This is only meaningful for key type
    ``text``. The default is 3.

  * ``label_columns_class`` (str): CSS class name added to the
    ``<div class="columns">`` element containing the label.

  * ``field_columns_class`` (str). CSS class name added to the
    ``<div class="columns">`` element containing the field.

  * ``helptext_position``: An optional name for the placement of helptext
    related to the question. Possible values are ``tooltip`` (showing the
    helptext as a tooltip on the question label)

  * ``helptext_length`` (int): Overwrite the default length (number of words) of
    the helptext shown initially (without the "See more" button).

  * ``label_position``: An optional name for the display and positioning of the
    label. Possible values are: ``placeholder`` (showing the label as a
    placeholder inside the input field)

  * ``conditions``: An optional list of conditions triggering
    conditional questions. Each condition must have the format
    ``""value_keyword|Boolean|key_keyword""``. Example::

      "conditions": ["value_15_1|True|key_16"]

    For the time being, conditions can only be set for Key
    (see :doc:`/configuration/key`) with type ``image_checkbox``.

  * ``conditional``: An optional boolean indicating whether this
    question is only shown depending on the condition (value) of another
    question. If set to ``true``, another question of this questiongroup
    should have the option ``conditions`` set.

    .. important::
        Questions with ``"conditional": true`` need to be listed **before**
        the question with ``"conditions": []`` triggering them.

  * ``questiongroup_conditions``: An optional list of conditions
    triggering conditional questiongroups. Each condition must have the
    format ``"expresssion|condition_name"`` where ``expression`` is part
    of a valid (Python and Javascript!) boolean expression and
    ``condition_name`` is the name of a Questiongroup's
    ``questiongroup_condition`` option.

    Example::

        "questiongroup_conditions": [">1|questiongroup_17", "<3|questiongroup_17"]

    .. seealso::
        :doc:`/configuration/questiongroup`
