"""
Minimal URL configuration for simplejwt_multisessions tests.
"""
from django.urls import path
from simplejwt_multisessions.api.views import (
    initializeSession,
    refreshSession,
    listOfActiveSessions,
    destroySessionById,
    destroyAllOtherSessions,
    logout,
)

urlpatterns = [
    path('api/session/login/',           initializeSession,       name='initialize_session'),
    path('api/session/refresh/',         refreshSession,          name='refresh_session'),
    path('api/session/list/',            listOfActiveSessions,    name='list_sessions'),
    path('api/session/destroy/',         destroySessionById,      name='destroy_session_by_id'),
    path('api/session/destroyAllOther/', destroyAllOtherSessions, name='destroy_all_other'),
    path('api/session/logout/',          logout,                  name='logout'),
]
