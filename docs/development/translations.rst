Translations
============

The source language of this project is *English*. Refer to the `django docs`_
for translations within django.

All fixtures for configurations and questionnaires are expected to have texts
at least in english.


Basics
------

* Translations are handled separately for the texts from django and
  questionnaires (see ``questionnaire.models.Translation``).
* Translation changes are expected to happen often, occasionally new languages
  will be introduced. Managing translations should require no effort from
  developers.
* These preconditions (handle translations for questionnaires in a jsonb-field,
  vs. gettext files django-translations) and the requirement for one system to
  handle all translations result in a workaround.
* po files and gettext are the 'default' way to handle translations.


Workflow
--------

* Create translation files for the website with ``makemessages``
* Translations from the database are exported into a .py file. ``pygettext``
  then creates a .pot file, ``msginit`` creates the language-specific po file.
  This process is automated (management command: ``translation_to_gettext``).
* Editing of both files is done within `Transifex`_. See the folder ``.tx`` in
  the project root for the transifex configuration.
* Updated translation files can be pulled with ``tx pull``
* Create new .mo files with ``compilemessages``
* The text changes for questionnaires and configurations are restored to the
  database with ``gettext_to_translation``.
* This process is automated with the command ``makemessages_plus``. A valid
  transifex account is required.
* This could be integrated in the deployment, but manual control is desired.


Todo
----

* Define the timing of translations with regard to git branches. Should
  translating be included when developing a new feature, or does translation
  'follow' after a feature is merged back to develop?
* Check if `txgh`_ would be helpful.


.. _django docs: https://docs.djangoproject.com/en/1.8/topics/i18n/translation/
.. _Transifex: https://www.transifex.com/university-of-bern-cde/qcat/
.. _txgh: https://github.com/transifex/txgh
