=========
Changelog
=========

All notable changes to this project will be documented here.
The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

`1.5`_ — 2026-05-15
--------------------

Added
~~~~~
- **Migrations** — ``simplejwt_multisessions`` now ships a proper initial
  migration (``0001_initial``).  Users upgrading from 1.4 should run
  ``python manage.py migrate simplejwt_multisessions`` after upgrading;
  the table schema is unchanged so no data is affected.
- **GitHub Actions CI** — matrix across Django 3.2 / 4.2 / 5.2 and
  Python 3.8 → 3.13 on every push and pull-request.
- **``test_settings.py`` + ``test_urls.py``** — standalone test harness;
  contributors can run the full suite without a host Django project.
- **``CONTRIBUTING.rst``** — setup, run, and PR guidelines for new contributors.
- **``tox.ini``** — local multi-version test runner.
- **``CHANGELOG.rst``** — this file.
- ``api/__init__.py`` package marker (previously missing).
- ``AuthenticationSession.__str__`` for friendlier admin and shell output.

Changed
~~~~~~~
- ``pyproject.toml``: dropped deprecated ``setuptools.build_meta:__legacy__``
  build backend; bumped ``setuptools`` requirement to ``>=61.0``.
- ``setup.cfg``: added ``djangorestframework >= 3.12`` to ``install_requires``
  (it was previously an undeclared transitive dependency); added Django 4.1,
  4.2, 5.0, 5.1, 5.2 and Python 3.11, 3.12, 3.13 classifiers; tightened
  ``python_requires`` to ``>=3.8`` (removed the micro-version pin ``3.8.5``).
- ``MANIFEST.IN`` renamed to ``MANIFEST.in`` (setuptools ignores the uppercase
  variant on case-sensitive file systems); contents updated to include all
  Python source files.
- README: requirements table updated to reflect supported versions; added
  badges, a security note for the ``SECRET`` pattern, and a testing section.

Fixed
~~~~~
- Removed unreachable dead-code block in ``SessionCreateSerializer.validate``
  (second ``if not self.user`` guard could never be reached).
- Removed unused ``from hashlib import new`` import in ``views.py``.
- Removed duplicate ``from django.contrib import admin`` import in ``admin.py``.
- Fixed typo ``'destory_all_other'`` → ``'destroy_all_other'`` in
  ``tests.py`` (caused one test to error instead of run).

`1.4`_ — 2022-09-14
--------------------

Added
~~~~~
- ``destroyAllOtherSessions`` API: destroy every active session except the
  caller's, optionally filtered by session type (``SHORT`` / ``LONG`` / ``ALL``).
- ``logout`` API: blacklist a refresh token and remove its session record
  without requiring an authenticated access token (uses ``secret_key`` instead).

Changed
~~~~~~~
- Improved README with full curl examples for every endpoint.

Fixed
~~~~~
- Various README formatting fixes.

`1.3`_ — 2022-09-11
--------------------

Added
~~~~~
- ``listOfActiveSessions`` API: returns active sessions per type with
  remaining slot count.
- ``destroySessionById`` API: revokes a single session by its ``session_id``.

`1.2`_ — 2022-09-08
--------------------

Added
~~~~~
- ``EXTEND_SESSION_ONCE_AFTER_EACH`` policy: extend the refresh token lifetime
  once after a configurable ``timedelta`` rather than on every request.
- ``LIMIT_NUMBER_OF_AVAIL_SESSIONS`` + ``MAX_NUMBER_ACTIVE_SESSIONS``:
  cap concurrent sessions per type.
- ``DESTROY_OLDEST_ACTIVE_SESSION``: automatically evict the oldest session
  when the cap is reached.

`1.1`_ — 2022-08-20
--------------------

Added
~~~~~
- ``SHORT`` / ``LONG`` dual-lifetime session model.
- ``ROTATE_REFRESH_TOKENS``, ``BLACKLIST_AFTER_ROTATION``,
  ``UPDATE_LAST_LOGIN``, ``EXTEND_SESSION``, ``EXTEND_SESSION_EVERY_TIME``
  per-session-type policies.
- ``initializeSession`` and ``refreshSession`` API views.

`1.0`_ — 2022-08-10
--------------------

Added
~~~~~
- Initial release: ``AuthenticationSession`` model wrapping
  ``djangorestframework-simplejwt`` refresh tokens with per-user session
  tracking.

.. _1.5: https://github.com/benyaamin/simplejwt_multisessions/compare/v1.4...v1.5
.. _1.4: https://github.com/benyaamin/simplejwt_multisessions/compare/v1.3...v1.4
.. _1.3: https://github.com/benyaamin/simplejwt_multisessions/compare/v1.2...v1.3
.. _1.2: https://github.com/benyaamin/simplejwt_multisessions/compare/v1.1...v1.2
.. _1.1: https://github.com/benyaamin/simplejwt_multisessions/compare/v1.0...v1.1
.. _1.0: https://github.com/benyaamin/simplejwt_multisessions/releases/tag/v1.0
