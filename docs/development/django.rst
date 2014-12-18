Django Snippets
===============

A collection of useful Django snippets.

Database migration
------------------

To detect the latest changes made to the data model and create a script
reflecting these changes, use::

    (env)$ python3 manage.py makemigrations

To apply the created migration script to a database, run::

    (env)$ python3 manage.py migrate


Fixtures
--------

Create fixture from database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage::

    (env)$ python3 manage.py dumpdata [appname] --indent 4 > [file]

Example::

    (env)$ python3 manage.py dumpdata configuration --indent 4 > sample.json

Load data from fixture
~~~~~~~~~~~~~~~~~~~~~~

Usage::

    (env)$ python3 manage.py loaddata [file]

Example::

    (env)$ python3 manage.py loaddata sample.json
