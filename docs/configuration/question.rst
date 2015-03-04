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
    # The key of the question.
    "key": "KEY",

    # (optional)
    "list_position": 1,

    "conditional": true,

    "conditions": [],
  }

.. seealso::
    For more information on the configuration of its child elements,
    please refer to their respective documentation:

    * :doc:`/configuration/key`
    * :doc:`/configuration/value`

    Also refer to the :ref:`configuration_questionnaire_example` of a
    Questionnaire configuration.


``key``
^^^^^^^

The keyword of the key of this question.

``list_position``
^^^^^^^^^^^^^^^^^

(Optional). An optional integer indicating if and at which position this
question should appear in the list representation of questionnaires. If
not set, the question will not appear in the list.

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
