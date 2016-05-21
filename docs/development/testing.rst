Testing
=======

Tests
-----

QCAT is tested using *functional tests* covering the interaction on the
web site and *unit tests* which test isolated pieces of the code.

.. important::
    The *functional tests* are based on Firefox. The
    `Selenium WebDriver`_ and its `Python bindings`_ used to run the
    tests do not suppor the latest (default) version of Firefox.

    Therefore, the functional tests are skipped by default. In order to
    run them, you need to first `download an older version of Firefox`_
    (e.g. version 28). Then you need to specify the path to this version
    of Firefox in your ``settings_local.py`` file, e.g.::

        TESTING_FIREFOX_PATH = '/path/to/old/version/of/firefox'

    .. _Selenium WebDriver: http://www.seleniumhq.org/
    .. _Python bindings: https://pypi.python.org/pypi/selenium
    .. _download an older version of Firefox: https://ftp.mozilla.org/pub/mozilla.org/firefox/releases/

Run all tests::

    (env)$ python3 manage.py test

Run only selected based on app::

    (env)$ python3 manage.py test accounts

Run only selected tests based on file path::

    (env)$ python3 manage.py test functional_tests.test_login

Run only selected tests based on attribute::

    (env)$ python3 manage.py test --attr=unit

    (env)$ python3 manage.py test --attr='!functional'

The following attributes are available: ``unit``, ``functional``.

To disable the output of logging information, use the flag
``--nologcapture``::

    (env)$ python3 manage.py test --nologcapture


Coverage
--------

You can measure the code coverage of your tests through `Coverage`_.

.. _Coverage: http://nedbatchelder.com/code/coverage/

Run the tests with coverage::

    (env)$ python3 manage.py test --with-coverage

This will create a report which can be found under
``coverage_html/index.html``.


Stress tests
------------

To check the performance of all parts, some stress tests are included. `Docker`_ is required to run them, the tests
are written with `locustio`_. To execute the tests, proceed as follows (from the project root)::

    (env)$ cd stress_tests
    (env)$ docker build -t locust .
    (env)$ docker run --rm -P locust

This starts a docker container with locust (on python 2.7). To start the test, the IP address of the docker container is
required (open a new terminal)::

    $ docker network inspect bridge

Get the IP for the running container and open the browser with <container ID>:8089 - the rest is managed in the browser.

When actively developing the locustfile, the ``stress_tests`` folder can be linked into the docker image::

    (env)$ docker run -v <path_to_qcat>/stress_tests:/locust -P locust --host=<your_host>

.. _Docker: https://www.docker.com/
.. _locustio: http://locust.io/
