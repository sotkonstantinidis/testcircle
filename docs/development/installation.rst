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

Git
^^^

The source code of QCAT is managed in `Git`_, a free and open source
distributed version control system.

.. _Git: http://git-scm.com/

Docker
^^^

Use the provided docker-compose file to create the environment. `Docker`_ and docker-compose
must be installed on your system.

.. _Docker: http://git-scm.com/


Preparation
^^^^^^^^^^^

Create a folder for the project::

    $ mkdir qcat && cd qcat

Get the code::

    $ git clone https://github.com/CDE-UNIBE/qcat.git .


Environment variables
^^^^^^^^^^^^^^^^^^^^^

Set following environment variables:

    * DJANGO_SETTINGS_MODULE
    * DJANGO_CONFIGURATION
    * DJANGO_SECRET_KEY

Run
^^^

Run the application::

    $ docker-compose up

If a database dump is available, copy it into the folder: /docker_compose/postgis/restore. Following file formats
are supported - keep in mind all files available are executed:

    * .sh
    * .sql
    * .sql.gz

If you want to build all requirements (static assets, elasticsearch, database), pass the 'build' param.::

    $ docker-compose run web build

Open your browser and go to http://0.0.0.0:8000 to see the project up and running.
