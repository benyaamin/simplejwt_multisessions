============================================================================================
simplejwt_multisessions: simpleJWT with session options plus two different refresh lifetimes
============================================================================================

simplejwt_multisessions is a Django app based on `djangorestframework-simplejwt` that allows you 
to generate SIMPLE_JWT with two different lifetimes and session features.

Introduction
------------

simplejwt_multisessions is an MIT licensed Django app that allows Django devs to generate refresh 
tokens with two different lifetimes i.e., "SHORT" and "LONG". simplejwt_multisessions is designed 
to manage tokens and sessions together. This app also can assign different policies to each type of lifetime category.

Why use simplejwt_multisessions?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Generates "LONG" and "SHORT" simpleJWT lifetime.
- Sets information of the session on the initialization. e.g., "Safari 15.6.1, iOS 15.6.1, iPhone"
- Extendable option for each session type with different policies.
    1. Extension of the session after each request by generating a new refresh token.
    2. Extension of the session once after each specific timedelta by generating a new refresh token.
- Limitable option for the available number of sessions. i.e., a User can log in as a "LONG" session 
    with only 3 different Endpoints/Devices or the User can log in as a "SHORT" session at the same 
    time with only 2 different Endpoints/Devices.
    1. Sets max number of available sessions for each session type: "SHORT", "LONG".
    2. Sets destroying oldest active sessions. i.e., if the user reaches the max number of active
    sessions then by logging a new session the oldest session will be destroyed.
- Returns list of active i.e., not expired sessions assigned to requested user with its `session_id`.
- Destroys sessions by their `session_id`.
- Destroys all other active/not expired sessions except the one making the request.
- Differentiable URLs for different APIs e.g., "login", "refresh", "list", "destroy", "destroyAllOther" and "logout".
- Most of API's permission_classes are set to `AllowAny` and need to receive `secret_key` in the body of the request 
    which is defined in settings of simplejwt_multisessions in settings.py and the rest are set to `IsAuthenticated`
    and need nothing else.

Requirements
~~~~~~~~~~~~

- `Python`_ 3.8+
- `Django`_ 3.2+
- `djangorestframework`_ 3.12+
- `djangorestframework-simplejwt`_ 5.0.0+

.. _Python: https://www.python.org/downloads/
.. _Django: https://www.djangoproject.com/download/
.. _djangorestframework: https://www.django-rest-framework.org/#installation
.. _djangorestframework-simplejwt: https://django-rest-framework-simplejwt.readthedocs.io/en/latest/

User guide
----------

Installation
~~~~~~~~~~~~

1. Install with pip:

.. code-block:: console

    $ python -m pip install simplejwt_multisessions

2. Clone the repo into your Django Project

https://github.com/benyaamin/simplejwt_multisessions

settings.py configuration 
~~~~~~~~~~~~~~~~~~~~~~~~~~

To start using simplejwt_multisessions, after installation of requirements first you should add 
`rest_framework_simplejwt.token_blacklist` to `INSTALLED_APPS` in `settings.py` and then add 
`simplejwt_multisessions` to it. 

.. code-block:: python

    # Django Project settings.py
    INSTALLED_APPS = [
        # ...
        "rest_framework_simplejwt.token_blacklist",
        "simplejwt_multisessions",
        # ...
    ]

According to djangorestframework-simplejwt configuration instruction:
https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html#project-configuration

.. code-block:: python

    # Django Project settings.py
    REST_FRAMEWORK = {
        # ...
        'DEFAULT_AUTHENTICATION_CLASSES': (
            # ...
            'rest_framework_simplejwt.authentication.JWTAuthentication'
        )
        # ...
    }

You also need to add djangorestframework-simplejwt settings to settings.py
https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html#settings

.. code-block:: python

    # Django project settings.py
    from datetime import timedelta
    #...

    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
        'ROTATE_REFRESH_TOKENS': False,
        'BLACKLIST_AFTER_ROTATION': False,
        'UPDATE_LAST_LOGIN': False,

        'ALGORITHM': 'HS256',
        'SIGNING_KEY': SECRET_KEY,
        'VERIFYING_KEY': None,
        'AUDIENCE': None,
        'ISSUER': None,
        'JWK_URL': None,
        'LEEWAY': 0,

        'AUTH_HEADER_TYPES': ('Bearer',),
        'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
        'USER_ID_FIELD': 'id',
        'USER_ID_CLAIM': 'user_id',
        'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

        'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
        'TOKEN_TYPE_CLAIM': 'token_type',
        'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

        'JTI_CLAIM': 'jti',

        'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
        'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
        'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    }

After adding SEIMPLE_JWT to your Django's settings.py, Now you are good to add simplejwt_multisessions's settings
to `settings.py`

.. code-block:: python

    # Django project settings.py
    JWT_MULTISESSIONS = {
        'SECRET': SECRET_KEY,
        'LONG_SESSION':{ # This section is the "LONG_SESSION" configuration.
            'REFRESH_TOKEN_LIFETIME': SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'], # or you can set the timedelta what you wish e.g., timedelta(days = 29)
            
            'ROTATE_REFRESH_TOKENS': False, # If set this flag true then after each token refresh request a new refresh token will be generated and the old one will be blacklisted
            'UPDATE_LAST_LOGIN': False, # By settings this flag to true after each request the session `lastUpdateDate` updates.
            'BLACKLIST_AFTER_ROTATION': False,

            'EXTEND_SESSION': True, # This flag specifies whether should extend the refresh lifetime after each refresh request or shouldn't
            'EXTEND_SESSION_EVERY_TIME': False, # If `EXTEND_SESSION` is set to true this flag specifies to extend refresh lifetime with the exact amount of `REFRESH_TOKEN_LIFETIME`
            'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(days= 15), # If `EXTEND_SESSION` is set to true but `EXTEND_SESSION_EVERY_TIME` is set to False, then the refresh token will be extended as much as this property specifies.
            
            'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True, # This feature decides to restrict the number of available sessions.
            'MAX_NUMBER_ACTIVE_SESSIONS': 5, # If `LIMIT_NUMBER_OF_AVAIL_SESSIONS` is set to true then this property defines the max number of active sessions and prevents requests to exceed more than its value.
            'DESTROY_OLDEST_ACTIVE_SESSION': True, # If `LIMIT_NUMBER_OF_AVAIL_SESSIONS` is set to true by setting this flag to true and the max number of requests exceeds `MAX_NUMBER_ACTIVE_SESSIONS` then the newly arrived request will destroy the oldest session and the new session will be initialized.
        }, 
        'SHORT_SESSION': { # This section is the "SHORT_SESSION" configuration. The features are as same as what is mentioned in the `LONG_SESSION` section.
            'REFRESH_TOKEN_LIFETIME': timedelta(days= 1),
            
            'ROTATE_REFRESH_TOKENS': False,
            'UPDATE_LAST_LOGIN': True,
            'BLACKLIST_AFTER_ROTATION': True,
            
            'EXTEND_SESSION': False,
            'EXTEND_SESSION_EVERY_TIME': False,
            'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(hours= 12),
            
            'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
            'MAX_NUMBER_ACTIVE_SESSIONS': 2,
            'DESTROY_OLDEST_ACTIVE_SESSION': True,
        }
    }

URLs
~~~~~

If you are intended to use `simplejwt_multisessions` you should instead of using URLs related to `rest_framework_simplejwt`
use the URLs mentioned below:

.. code-block:: python
    
    # <root_of_your_django_project>/urls.py
    #...
    from simplejwt_multisessions.api.views import (
                                                initializeSession, 
                                                refreshSession,
                                                listOfActiveSessions,
                                                destroySessionById,
                                                destroyAllOtherSessions,
                                                logout,
                                                )
    #...
    urlpatterns = [
        ...    
        path('api/session/login/',              initializeSession,          name='initialize_session'),
        path('api/session/refresh/',            refreshSession,             name='refresh_session'),
        path('api/session/list/',               listOfActiveSessions,       name='list_sessions'),
        path('api/session/destroy/',            destroySessionById,         name='destroy_session_by_id'),
        path('api/session/destroyAllOther/',    destroyAllOtherSessions,    name="destroy_all_other"),
        path('api/session/logout/',             logout,                     name='logout'),
        #...
    ] 


Usage
------

Login and Refresh
~~~~~~~~~~~~~~~~~~

For logging in or initializing a new session you need five variables to mention in your request's body:
    1. `username`: The username_field of the Django user model
    2. `password`: The password of the Django user model
    3. `secret_key`: The secret_key mentioned in JWT_MULTISESSIONS settings in `settings.py`
    4. `session`: The session type of the request options: ["LONG", "SHORT"]
    5. `info`: This field can store arbitrary information about the session. for instance Device id or browser version or IP address e.g., "Safari 15.6.1, iOS 15.6.1, iPhone". NOTICE: This field is not changeable after initialization.

.. code-block:: console

    curl \
        -X POST \
        -H "Content-Type: application/json" \
        -d '{"username": "benyamin", "password": "somepassword",
        "secret_key": "the_Secret_Key", "session": "LONG",
        "info": "sample info"}' \
        http://localhost:8000/api/session/login/

    ...
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY2NTc1OTU2MywiaWF0IjoxNjYzMTY3NTYzLCJqdGkiOiJkOWFiYTMzYWNmMDg0ODU2YjJjMjA4OWJiYTFjZDc0YSIsInVzZXJfaWQiOjF9.zGwSDoJzoCEhIqwg3D4bRAwrnJ0DKRKSGOzdyyw__ho",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYzMTY4MTYzLCJpYXQiOjE2NjMxNjc1NjMsImp0aSI6IjBlZGZlMmY3MzhiMzRhOWFhYzQ4ZDhjYzAxOTVmZjEzIiwidXNlcl9pZCI6MX0.QCEqyFmXk5-yHZ4dYKnhNx80o9mgAYRdgFfUtgV1lQQ",
        "session_id": "ozdyyw__ho-10"
    }

Same as classic `simpleJWT` You can use the returned access token to prove authentication for a protected view:

.. code-block:: console

    curl \
    -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYzMTY4MTYzLCJpYXQiOjE2NjMxNjc1NjMsImp0aSI6IjBlZGZlMmY3MzhiMzRhOWFhYzQ4ZDhjYzAxOTVmZjEzIiwidXNlcl9pZCI6MX0.QCEqyFmXk5-yHZ4dYKnhNx80o9mgAYRdgFfUtgV1lQQ" \
    http://localhost:8000/api/some-protected-view/

When this access token expires, you can use the refresh token to obtain another access token:
NOTICE: 
1. Since refresh API's `permission_classes` is `AllowAny` you need to enter the `secret_key` that is assigned in simplejwt_multisessions's settings in `settings.py`.
2. You should enter `"session"` in your request's body. This `"session"` must be the same as the one you used in the login request otherwise the session will be destroyed.

.. code-block:: console

    curl \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"refresh":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY2NTc1OTU2MywiaWF0IjoxNjYzMTY3NTYzLCJqdGkiOiJkOWFiYTMzYWNmMDg0ODU2YjJjMjA4OWJiYTFjZDc0YSIsInVzZXJfaWQiOjF9.zGwSDoJzoCEhIqwg3D4bRAwrnJ0DKRKSGOzdyyw__ho",
         "secret_key": "the_Secret_Key", "session": "LONG"}' \
    http://localhost:8000/api/session/refresh/
    
    ...
    {"access":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYzMTcwNTA5LCJpYXQiOjE2NjMxNjc1NjMsImp0aSI6IjQxNWMxNjcwMmVkNTRkYWM5MDk0OTkyMmExMjcyMTdjIiwidXNlcl9pZCI6MX0.gdSQUmoSt_-ir87xngbC7YIvwNsAXJaAy0l4IRfuT1I"}

List of all sessions
~~~~~~~~~~~~~~~~~~~~~

To see the list of user's all active sessions you can use the list's API.
You have to enter `"session"` in the body of your request. `"session"` can be one of these options: `["SHORT", "LONG", "ALL"]`
1. If you ask for `"SHORT"` sessions, in return you will just see the list of all short types of sessions and related info.
2. If you ask for `"LONG"` sessions, in return you will just see the list of all long types of sessions and related info.
3. If you ask for `"ALL"` sessions, in return you will see the list of all types of sessions and related info, and by `"ALL"`, it means `"SHORT"` and `"LONG"` sessions in total.
NOTICE: Since this API's `permission_classes` is set to `IsAuthenticated` the proof of authentication is mandatory.

1. `"session": "SHORT"`

.. code-block:: console
    
    curl \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYzMTY4MTYzLCJpYXQiOjE2NjMxNjc1NjMsImp0aSI6IjBlZGZlMmY3MzhiMzRhOWFhYzQ4ZDhjYzAxOTVmZjEzIiwidXNlcl9pZCI6MX0.QCEqyFmXk5-yHZ4dYKnhNx80o9mgAYRdgFfUtgV1lQQ" \
    -d '{"session":"SHORT"}' \
    http://localhost:8000/api/session/list/
    

.. code-block:: text

    {
        "Short":
            {
                "Available Sessions":"0",
                "Sessions":[
                    {
                        "session_id":"8e_ikeorsa-8",
                        "created_at":"2022-09-11T11:16:26Z",
                        "last_update":"2022-09-14T14:41:26Z",
                        "expires_at":"2022-09-15T14:41:26Z",
                        "session_info":"Safari 15.6.1, iOS 15.6.1, iPhone"
                    },
                    {
                        "session_id":"oetqjgyp1o-9",
                        "created_at":"2022-09-14T08:23:14Z",
                        "last_update":"2022-09-14T14:41:20Z",
                        "expires_at":"2022-09-15T14:41:20Z",
                        "session_info":"Chrome 105.0.0.0, OS X 10.15.7 64-bit"
                    }
                ]
            }
    }

2. `"session": "LONG"`

.. code-block:: console
    
    curl \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYzMTY4MTYzLCJpYXQiOjE2NjMxNjc1NjMsImp0aSI6IjBlZGZlMmY3MzhiMzRhOWFhYzQ4ZDhjYzAxOTVmZjEzIiwidXNlcl9pZCI6MX0.QCEqyFmXk5-yHZ4dYKnhNx80o9mgAYRdgFfUtgV1lQQ" \
    -d '{"session":"LONG"}' \
    http://localhost:8000/api/session/list/

.. code-block:: text

    {
        "Long":
            {
                "Available Sessions":"2",
                "Sessions":[
                    {
                        "session_id": "8oeptkbkk0-3",
                        "created_at": "2022-09-08T19:14:33Z",
                        "last_update": "2022-09-08T19:14:33.108983Z",
                        "expires_at": "2022-10-08T19:14:33Z",
                        "session_info": "iOS native app, V1.0.2"
                    },
                    {
                        "session_id": "sppfiktswq-4",
                        "created_at": "2022-09-08T19:14:59Z",
                        "last_update": "2022-09-08T19:14:59.905518Z",
                        "expires_at": "2022-10-08T19:14:59Z",
                        "session_info": "android native app, V1.4"
                    },
                    {
                        "session_id": "rvu6qdlcdc-5",
                        "created_at": "2022-09-08T19:15:22Z",
                        "last_update": "2022-09-08T19:15:22.407307Z",
                        "expires_at": "2022-10-08T19:15:22Z",
                        "session_info": "react native app, V2.5"
                    },
                ]
            }
    }

3. `"session": "ALL"`

.. code-block:: console
    
    curl \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYzMTY4MTYzLCJpYXQiOjE2NjMxNjc1NjMsImp0aSI6IjBlZGZlMmY3MzhiMzRhOWFhYzQ4ZDhjYzAxOTVmZjEzIiwidXNlcl9pZCI6MX0.QCEqyFmXk5-yHZ4dYKnhNx80o9mgAYRdgFfUtgV1lQQ" \
    -d '{"session":"ALL"}' \
    http://localhost:8000/api/session/list/
    
.. code-block:: text

    {
        "Short":
            {
                "Available Sessions":"0",
                "Sessions":[
                    {
                        "session_id":"8e_ikeorsa-8",
                        "created_at":"2022-09-11T11:16:26Z",
                        "last_update":"2022-09-14T14:41:26Z",
                        "expires_at":"2022-09-15T14:41:26Z",
                        "session_info":"Safari 15.6.1, iOS 15.6.1, iPhone"
                    },
                    {
                        "session_id":"oetqjgyp1o-9",
                        "created_at":"2022-09-14T08:23:14Z",
                        "last_update":"2022-09-14T14:41:20Z",
                        "expires_at":"2022-09-15T14:41:20Z",
                        "session_info":"Chrome 105.0.0.0, OS X 10.15.7 64-bit"
                    }
                ]
            },
        "Long":
            {
                "Available Sessions":"2",
                "Sessions":[
                    {
                        "session_id": "8oeptkbkk0-3",
                        "created_at": "2022-09-08T19:14:33Z",
                        "last_update": "2022-09-08T19:14:33.108983Z",
                        "expires_at": "2022-10-08T19:14:33Z",
                        "session_info": "iOS native app, V1.0.2"
                    },
                    {
                        "session_id": "sppfiktswq-4",
                        "created_at": "2022-09-08T19:14:59Z",
                        "last_update": "2022-09-08T19:14:59.905518Z",
                        "expires_at": "2022-10-08T19:14:59Z",
                        "session_info": "android native app, V1.4"
                    },
                    {
                        "session_id": "rvu6qdlcdc-5",
                        "created_at": "2022-09-08T19:15:22Z",
                        "last_update": "2022-09-08T19:15:22.407307Z",
                        "expires_at": "2022-10-08T19:15:22Z",
                        "session_info": "react native app, V2.5"
                    },
                ]
            }
    }

Destroy session by their id
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes End-User wants to terminate one of its active sessions. This action can be done by knowing the `"session_id"` 
and using `'destroy'`'s API.
NOTICE: Since this API's `permission_classes` is set to `IsAuthenticated` the proof of authentication is mandatory.

.. code-block:: console
    
    curl \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYzMTY4MTYzLCJpYXQiOjE2NjMxNjc1NjMsImp0aSI6IjBlZGZlMmY3MzhiMzRhOWFhYzQ4ZDhjYzAxOTVmZjEzIiwidXNlcl9pZCI6MX0.QCEqyFmXk5-yHZ4dYKnhNx80o9mgAYRdgFfUtgV1lQQ" \
    -d '{"session_id":"rvu6qdlcdc-5"}' \
    http://localhost:8000/api/session/destroy/
    
.. code-block:: text

    {}

Destroy all other sessions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This API allows the End-User to destroy all other active sessions except the one that makes the request.
Necessary inputs: `["session", "refresh"]`. `"session"` specifies the session type to be destroyed.
`"refresh"` specifies the considered `"refresh"` token assigned to the current request session and is excluded from being destroyed.
NOTICE: Since this API's `permission_classes` is set to `IsAuthenticated` the proof of authentication is mandatory.

1. `"session": "SHORT"`

.. code-block:: console
    
    curl \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYzMTY4MTYzLCJpYXQiOjE2NjMxNjc1NjMsImp0aSI6IjBlZGZlMmY3MzhiMzRhOWFhYzQ4ZDhjYzAxOTVmZjEzIiwidXNlcl9pZCI6MX0.QCEqyFmXk5-yHZ4dYKnhNx80o9mgAYRdgFfUtgV1lQQ" \
    -d '{"session":"SHORT",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY2NTc1OTU2MywiaWF0IjoxNjYzMTY3NTYzLCJqdGkiOiJkOWFiYTMzYWNmMDg0ODU2YjJjMjA4OWJiYTFjZDc0YSIsInVzZXJfaWQiOjF9.zGwSDoJzoCEhIqwg3D4bRAwrnJ0DKRKSGOzdyyw__ho"}' \
    http://localhost:8000/api/session/destroyAllOther/
    
.. code-block:: text

    {}

2. `"session": "LONG"`

.. code-block:: console
    
    curl \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYzMTY4MTYzLCJpYXQiOjE2NjMxNjc1NjMsImp0aSI6IjBlZGZlMmY3MzhiMzRhOWFhYzQ4ZDhjYzAxOTVmZjEzIiwidXNlcl9pZCI6MX0.QCEqyFmXk5-yHZ4dYKnhNx80o9mgAYRdgFfUtgV1lQQ" \
    -d '{"session":"LONG",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY2NTc1OTU2MywiaWF0IjoxNjYzMTY3NTYzLCJqdGkiOiJkOWFiYTMzYWNmMDg0ODU2YjJjMjA4OWJiYTFjZDc0YSIsInVzZXJfaWQiOjF9.zGwSDoJzoCEhIqwg3D4bRAwrnJ0DKRKSGOzdyyw__ho"}' \
    http://localhost:8000/api/session/destroyAllOther/
    
.. code-block:: text

    {}

3. `"session": "ALL"`

.. code-block:: console
    
    curl \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjYzMTY4MTYzLCJpYXQiOjE2NjMxNjc1NjMsImp0aSI6IjBlZGZlMmY3MzhiMzRhOWFhYzQ4ZDhjYzAxOTVmZjEzIiwidXNlcl9pZCI6MX0.QCEqyFmXk5-yHZ4dYKnhNx80o9mgAYRdgFfUtgV1lQQ" \
    -d '{"session":"ALL",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY2NTc1OTU2MywiaWF0IjoxNjYzMTY3NTYzLCJqdGkiOiJkOWFiYTMzYWNmMDg0ODU2YjJjMjA4OWJiYTFjZDc0YSIsInVzZXJfaWQiOjF9.zGwSDoJzoCEhIqwg3D4bRAwrnJ0DKRKSGOzdyyw__ho"}' \
    http://localhost:8000/api/session/destroyAllOther/
    
.. code-block:: text

    {}

Logout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This API facilitates logging out the session.
Necessary inputs: `["secret_key", "refresh"]`. The secret_key mentioned in JWT_MULTISESSIONS settings in settings.py.
`"refresh"` must be the refresh token the one that makes the request and is about to log out.

.. code-block:: console
    
    curl \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"secret_key": "the_Secret_Key",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY2NTc1OTU2MywiaWF0IjoxNjYzMTY3NTYzLCJqdGkiOiJkOWFiYTMzYWNmMDg0ODU2YjJjMjA4OWJiYTFjZDc0YSIsInVzZXJfaWQiOjF9.zGwSDoJzoCEhIqwg3D4bRAwrnJ0DKRKSGOzdyyw__ho"}' \
    http://localhost:8000/api/session/logout/
    
.. code-block:: text

    {}


License
-------

The licenses of `djangorestframework` and `djangorestframework-simplejwt` projects have been included in this repository in the “licenses” directory.

.. code-block:: text

        MIT License

        Copyright (c) 2022 Benyamin Agha Ebrahimi

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
