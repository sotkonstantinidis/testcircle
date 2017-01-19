Summary
=======

This describes the ideas and workflow of how questionnaires are exported as pdf.
As of now, there is only one type of summary which displays the questionnaire
in full - so its not actually a summary but just a pdf-export.

Following changes are planned:

* Users should be able to select/deselect sections on the pdf (description,
  location, etc.)
* Changes in the output format (A6) should be configurable


Idea and rationale
------------------

The summary is not a fixed (hard coded) view, but its content may change
depending on configuration and version of the config.

The relevant sections for the summary of each questionnaire are defined in the
config. Gathering data for the summary happens in two steps:

* get combined data from config and questionnaire (use the same functionality
  as the questionnaire API resource)
* filter, aggregate and annotate data specifically for the summary

This data is passed to a view as JSON, where its contents are extracted to HTML
depending on its type. This extraction happens with frontend technologies.

The created HTML is then converted to PDF with wkhtmltopdf. This library was
selected based on a demo-HTML / proof of concept.

This concept of creating JSON and extract it to HTML was decided upon because:

* Work can be sourced to external colleagues
* Robust handling of data (questionnaires will change)
* More 'modules' (=types that can be extracted from JSON to HTML) can be added
  later
* HTML can be converted to different formats (doc) as well
* The very first step of combining data from config and questionnaire was
  required for another project as well


Technical workflow
------------------

* The view ```questionnaire.views.QuestionnaireSummaryPDFCreateView``` is called
* Data for the summary is created with
  ```questionnaire.summary_data_provider.get_summary_data```. This returns the
  data as set up by the provider according to summary type and configuration.
  As of now, only the type 'full' exists, but more types (4 page, 1 page, etc.)
  are requested.
* In the ```get_summary_data method```, the questionnaire and configuration
  data is combined with the same class built for the questionnaire detail API
  resource: ```configuration.configured_questionnaire.ConfiguredQuestionnaire```
* The full data is then reduced in two steps:

  * Select only data as defined by the configuration. The attribute:
    'summary' defines the section on the summary (e.g. description,
    location)
  * todo: fill up when tables are ready
