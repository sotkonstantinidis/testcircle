Questionnaire Configuration
===========================

The configuration of a Questionnaire is stored in a JSON format in the ``data`` field of :class:`configuration.models.Configuration`.

Format
------

The basic format of the configuration is as follows::

  {
    # See class QuestionnaireCategory for the format of categories.
    "categories": [
      {
        # The keyword of the category.
        "keyword": "CAT_KEYWORD",

        # See class QuestionnaireSubcategory for the format of subcategories.
        "subcategories": [
          {
            # The keyword of the subcategory.
            "keyword": "SUBCAT_KEYWORD",

            # See class QuestionnaireQuestiongroup for the format of
            # questiongroups.
            "questiongroups": [
              {
                # The keyword of the questiongroup.
                "keyword": "QUESTIONGROUP_KEYWORD",

                # (optional)
                "template": "TEMPLATE_NAME",

                # (optional)
                "min_num": 1,

                # (optional)
                "max_num": 1,

                # See class QuestionnaireQuestion for the format of questions.
                "questions": [
                  {
                    # The key of the question.
                    "key": "KEY"
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }

.. seealso::
    :class:`configuration.configuration.QuestionnaireSubcategory`

.. seealso::
    :class:`configuration.configuration.QuestionnaireQuestiongroup`

.. seealso::
    :class:`configuration.configuration.QuestionnaireQuestion`


Example
-------

The following is an arbitrary example of how a configuration could look like::

  {
    "categories": [
      {
        "keyword": "cat_1",
        "subcategories": [
          {
            "keyword": "subcat_1_1",
            "questiongroups": [
              {
                "questions": [
                  {
                    "key": "key_1",
                    "list_position": 2
                  },
                  {
                    "key": "key_3"
                  }
                ],
                "keyword": "qg_1"
              },
              {
                "questions": [
                  {
                    "key": "key_2"
                  }
                ],
                "keyword": "qg_2"
              }
            ]
          },
          {
            "keyword": "subcat_1_2",
            "questiongroups": [
              {
                "questions": [
                  {
                    "key": "key_4"
                  }
                ],
                "keyword": "qg_3"
              }
            ]
          }
        ]
      },
      {
        "keyword": "cat_2",
        "subcategories": [
          {
            "keyword": "subcat_2_1",
            "questiongroups": [
              {
                "questions": [
                  {
                    "key": "key_5",
                    "list_position": 1
                  }
                ],
                "keyword": "qg_4",
                "max_num": 2
              }
            ]
          }
        ]
      },
      {
        "keyword": "cat_3",
        "subcategories": [
          {
            "keyword": "subcat_3_1",
            "questiongroups": [
              {
                "questions": [
                  {
                    "key": "key_7"
                  }
                ],
                "keyword": "qg_5",
                "template": "inline_1"
              }, {
                "questions": [
                  {
                    "key": "key_8"
                  }
                ],
                "keyword": "qg_6",
                "template": "inline_1",
                "max_num": 3
              }
            ]
          },
          {
            "keyword": "subcat_3_2",
            "questiongroups": [
              {
                  "questions": [
                  {
                    "key": "key_9"
                  }
                ],
                "keyword": "qg_7",
                "template": "inline_1",
                "min_num": 2
              }, {
                "questions": [
                  {
                    "key": "key_10"
                  }
                ],
                "keyword": "qg_8",
                "template": "inline_1",
                "max_num": 3,
                "min_num": 2
              }
            ]
          }
        ]
      }
    ]
  }
