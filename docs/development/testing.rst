Testing
=======

Tests
-----

QCAT is tested using *functional tests* covering the interaction on the
web site and *unit tests* which test isolated pieces of the code.

Run all tests::

    (env)$ python3 manage.py test

Run only selected based on app::

    (env)$ python3 manage.py test accounts

Run only selected tests based on file path::

    (env)$ python3 manage.py test functional_tests.test_login


Coverage
--------

You can measure the code coverage of your tests through `Coverage`_.

.. _Coverage: http://nedbatchelder.com/code/coverage/

Run the tests with coverage::

    (env)$ python3 manage.py test --with-coverage

This will create a report which can be found under
``coverage_html/index.html``.
