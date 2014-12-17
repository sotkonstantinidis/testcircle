Django Snippets
===============

.. role:: bash(code)
   :language: bash

A collection of useful Django snippets.

Database migration
------------------

    :bash:`(env)$ python3 manage.py makemigrations`

    :bash:`(env)$ python3 manage.py syncdb`


Fixtures
--------

Create fixture from database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage:
    :bash:`(env)$ python3 manage.py dumpdata [appname] --indent 4 > [file]`

Example:
    :bash:`(env)$ python3 manage.py dumpdata configuration --indent 4 > sample.json`

Load data from fixture
~~~~~~~~~~~~~~~~~~~~~~

Usage:
    :bash:`(env)$ python3 manage.py loaddata [file]`

Example:
    :bash:`(env)$ python3 manage.py loaddata sample.json`
