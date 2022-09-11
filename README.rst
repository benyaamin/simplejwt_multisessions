=====
simplejwt_multisessions
=====

simplejwt_multisessions is a Django app that allows you to generate SIMPLE_JWT with 
two different lifetimes plus more options.

options:
1- Two Different lifetimes
2- Set Limitation on number available sessions
3- Limitation Policies e.g., Destroy oldest sessions or not


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
