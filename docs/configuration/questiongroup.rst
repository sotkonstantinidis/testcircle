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
    "view_options": {
      # Default: "default"
      "template": "TEMPLATE_NAME",

      # Default: ""
      "extra": "measure_other",

      # Default: ""
      "colclass": "top-margin"
    },

    # (optional)
    "form_options": {
      # Default: "default"
      "template": "TEMPLATE_NAME",

      # Default: 1
      "min_num": 2,

      # Default: 1
      "max_num: 3,

      # Default: ""
      "numbered": "NUMBERED",

      # Default: ""
      "detail_level": "DETAIL_LEVEL",

      # Default: ""
      "questiongroup_condition": "CONDITION_NAME",
    },

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


``view_options``
^^^^^^^^^^^^^^^^

(Optional). An optional object containing configuration options for the
view representation of the questiongroup.

  * ``template``: An optional template name. Must be a valid file name
    with ``.html`` ending in folder
    ``templates/details/questiongroup/``.

  * ``extra``: TODO

  * ``colclass``: An optional name of a CSS class to be passed to the
    column of the Questiongroup in the template.


``form_options``
^^^^^^^^^^^^^^^^

(Optional). An optional object containing configuration options for the
form representation of the question.

  * ``template``: An optional template name. Must be a valid file name
    with ``.html`` ending in folder ``templates/form/questiongroup/``.

  * ``min_num``: The minimum for repeating questiongroups to appear.
    Defaults to 1.

  * ``max_num``: The maximum for repeating questiongroups to appear. If
    larger than ``min_num``, buttons to add or remove questiongroups
    will be rendered in the form. Defaults to ``min_num``.

  * ``numbered``: An optional parameter if the questiongroup is to be
    numbered. Possible values are ``inline`` (numbering inside field
    label) or ``prefix`` (numbering indented before fields). If not
    specified, no numbering is used.

    .. hint::
        If possible, ``prefix`` should be used.

  * ``detail_level``: An optional parameter if the questiongroup
    contains additional, mostly more detailed questions which are only
    visible after clicking on a link. This is used for the
    "Plus"-Questions. The value of the parameter can be freely chosen.

  * ``questiongroup_condition``: An optional name of a condition valid
    for this questiongroup. The name must correspond to one of
    ``questiongroup_conditions`` of a Question configuration.

    .. seealso::
        :doc:`/configuration/question`


``questions``
^^^^^^^^^^^^^

A list of :doc:`/configuration/question`.
