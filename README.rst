=====
simplejwt_multisessions
=====

simplejwt_multisessions is a Django app to conduct web-based simplejwt_multisessions. 
For each question,
visitors can choose between a fixed number of answers.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "simplejwt_multisessions" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'simplejwt_multisessions',
    ]

2. Include the polls URLconf in your project urls.py like this::

from simplejwt_multisessions.api.views          import (
                                                initializeSession, 
                                                refreshSession,
                                                listOfActiveSessions,
                                                destroySessionById,
                                                destroyAllOtherSessions,
                                                logout,
                                                )
    ...

urlpatterns = [
    ...
    path('api/session/login/',              initializeSession,          name='initialize_session'),
    path('api/session/refresh/',            refreshSession,             name='refresh_session'),
    path('api/session/list/',               listOfActiveSessions,       name='list_sessions'),
    path('api/session/destroy/',            destroySessionById,         name='destroy_session_by_id'),
    path('api/session/destroyAllOther/',    destroyAllOtherSessions,    name="destory_all_other"),
    path('api/session/logout/',             logout,                     name='logout'),
    ...
]

3. Run ``python manage.py migrate`` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
