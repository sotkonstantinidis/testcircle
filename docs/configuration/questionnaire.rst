Configuration of the Questionnaire
==================================

The configuration of the Questionnaires is stored in a JSON format.

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
                "keyword": "qg_1",
                "questions": [
                  {
                    "key": "key_1"
                  }, {
                    "key": "key_3"
                  }
                ]
              }, {
                "keyword": "qg_2",
                "questions": [
                  {
                    "key": "key_2"
                  }
                ]
              }
            ]
          }, {
            "keyword": "subcat_1_2",
            "questiongroups": [
              {
                "keyword": "qg_3",
                "questions": [
                  {
                    "key": "key_4"
                  }
                ]
              }
            ]
          }
        ]
      }, {
        "keyword": "cat_2",
        "subcategories": [
          {
            "keyword": "subcat_2_1",
            "questiongroups": [
              {
                "keyword": "qg_4",
                "questions": [
                  {
                    "key": "key_5"
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
