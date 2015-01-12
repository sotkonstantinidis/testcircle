Installation
============

This section covers the installation of QCAT for local development. For
instructions on how to deploy QCAT to a server, refer to the
`Deployment`_ section.

.. _Deployment: deployment.html

Prerequisites
-------------

The following prerequisites are needed:

* `Python 3`_
* `Git`_
* `PostgreSQL`_ (at least version 9.4 as the JSON-B data type is needed)

.. _Python 3: http://python.org/
.. _Git: http://git-scm.com/
.. _PostgreSQL: http://www.postgresql.org/

Installation on a UNIX system
-----------------------------

These instructions will take you through the process of installing QCAT
on your computer, assuming that you are running a UNIX system (for
example Ubuntu).

Create a folder for the project and create a virtual environment in it::

    $ virtualenv --python=python3 env

Get the code::

    $ git clone https://github.com/CDE-UNIBE/qcat.git

Switch to the source folder, activate the virtual environment and
install the dependencies::

    $ cd qcat
    $ source ../env/bin/activate
    (env)$ pip3 install -r requirements.txt

Create and set up a database (with PostGIS extension).

Copy the sample local settings file and adapt it. Especially specify the
database connection! ::

    $ cp qcat/settings_local.py.sample qcat/settings_local.py
    $ vim qcat/settings_local.py

Let Django create the database tables for you::

    (env)$ python3 manage.py migrate

Load the initial data of QCAT::

    (env)$ python3 manage.py load_qcat_data

Run the application::

    (env)$ python3 manage.py runserver

Open your browser and go to http://localhost:8000 to see if everything
worked.
