============
Contributing
============

Thank you for considering a contribution to **simplejwt_multisessions**!
This document covers everything you need to go from zero to a merged PR.

Setting up a development environment
-------------------------------------

.. code-block:: console

    # 1. Fork & clone
    $ git clone https://github.com/<your-username>/simplejwt_multisessions.git
    $ cd simplejwt_multisessions

    # 2. Create a virtual environment
    $ python -m venv .venv
    $ source .venv/bin/activate          # Windows: .venv\Scripts\activate

    # 3. Install all dependencies
    $ pip install django djangorestframework djangorestframework-simplejwt

    # Optional: install tox for multi-version testing
    $ pip install tox

Running the test suite
-----------------------

A standalone Django settings file and URL conf are included so you don't
need a host project:

.. code-block:: console

    $ DJANGO_SETTINGS_MODULE=test_settings python -m django test \
          simplejwt_multisessions.tests -v 2

All 9 tests should pass.  Please ensure they still pass before opening a PR.

Multi-version testing with tox
--------------------------------

.. code-block:: console

    $ tox                      # run all envs
    $ tox -e py312-django52    # run a single env

See ``tox.ini`` for the full environment matrix.

Code style
-----------

- Follow PEP 8.
- Keep lines ≤ 100 characters.
- No unused imports (the CI will catch them).

Opening a pull request
-----------------------

1. Branch off ``main``: ``git checkout -b feature/my-change``
2. Make your changes and add tests where appropriate.
3. Run the test suite locally and confirm it is green.
4. Update ``CHANGELOG.rst`` under an ``Unreleased`` section.
5. Push your branch and open a PR against ``main``.

Reporting issues
-----------------

Please use the `GitHub issue tracker <https://github.com/benyaamin/simplejwt_multisessions/issues>`_
and include:

- Django / DRF / simplejwt versions
- Python version
- A minimal reproduction case
- The full traceback if applicable

Security disclosures
---------------------

Please **do not** open a public issue for security vulnerabilities.
Email ``Benyamin.eb@gmail.com`` directly with the details and we will
coordinate a fix and disclosure together.
