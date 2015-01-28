Installation
============

This section covers the installation of QCAT for local development. For
instructions on how to deploy QCAT to a server, refer to the
`Deployment`_ section.

.. _Deployment: deployment.html


Prerequisites
-------------

The following prerequisites are needed. Make sure to have them installed
on your system.

Python 3
^^^^^^^^

QCAT is written in `Python 3`_, which is already installed on many
operating systems.

Git
^^^

The source code of QCAT is managed in `Git`_, a free and open source
distributed version control system.

PostgreSQL
^^^^^^^^^^

`PostgreSQL`_ is the database management system behind QCAT. In order to
install QCAT, you need to create a database first and install the
`PostGIS`_ extension for this database.

.. important::
    At least version 9.4 of PostgreSQL is needed as support of the
    JSON-B data type is required.

.. _Python 3: http://python.org/
.. _Git: http://git-scm.com/
.. _PostgreSQL: http://www.postgresql.org/
.. _PostGIS: http://postgis.net/


Installation on a UNIX system
-----------------------------

These instructions will take you through the process of installing QCAT
on your computer, assuming that you are running a UNIX system (for
example Ubuntu).

Preparation
^^^^^^^^^^^

Create a folder for the project and create a virtual environment in it::

    $ virtualenv --python=python3 env

Get the code::

    $ git clone https://github.com/CDE-UNIBE/qcat.git

Installation: Application
^^^^^^^^^^^^^^^^^^^^^^^^^

Switch to the source folder, activate the virtual environment and
install the dependencies::

    $ cd qcat
    $ source ../env/bin/activate
    (env)$ pip3 install -r requirements.txt

.. hint::
    If the installation of the requirements produces errors concerning
    psycopg2, make sure you have the ``python3-dev`` package installed::

        sudo apt-get install python3-dev

Create and set up a database (with PostGIS extension).

Copy the sample local settings file and adapt it. Especially specify the
database connection! ::

    $ cp qcat/settings_local.py.sample qcat/settings_local.py
    $ vim qcat/settings_local.py

Let Django create the database tables for you::

    (env)$ python3 manage.py migrate

..
    Collect the static files needed by Django::

        (env)$ python3 manage.py collectstatic


Load the initial data of QCAT::

    (env)$ python3 manage.py load_qcat_data


Installation: Static files
^^^^^^^^^^^^^^^^^^^^^^^^^^

The static files (such as CSS or JavaScript files and libraries) are
managed using `Bower`_ and `GruntJS`_, both requiring the `NodeJS`_
platform.

.. _Bower: http://bower.io/
.. _GruntJS: http://gruntjs.com/
.. _NodeJS: http://nodejs.org/

Install NodeJS and its package manager::

    sudo apt-get install nodejs nodejs-legacy npm

Use NPM to install Bower and Grunt::

    sudo npm install -g grunt-cli bower

Install the project dependencies::

    sudo npm install

Let Bower collect the required libraries::

    bower install

Use Grunt to build the static files::

    grunt build

.. hint::
    See the documentation on :doc:`grunt` for additional grunt commands.


Run
^^^

Run the application::

    (env)$ python3 manage.py runserver

Open your browser and go to http://localhost:8000 to see if everything
worked.
