'''

Created By Benyamin, 10 Aug 2022


'''
from datetime                                           import datetime
from django.utils.timezone                              import make_aware
from django.template.defaultfilters                     import slugify
from django.utils                                       import timezone
from django.contrib.auth                                import get_user_model
from rest_framework_simplejwt.tokens                    import RefreshToken
from django.db.models                                   import Q
from ..models                                           import (
                                                                AuthenticationSession,
                                                            )
from .serializers                                      import (
                                                                SessionCreateSerializer,
                                                                SessionRefresh,
                                                                ListRequestSerializer,
                                                                DestroySessionSerializer,
                                                                LogoutSessionSerializer,
                                                                DestroyAllOtherSessionsSerializer
                                                            )
from rest_framework                                     import  status

from rest_framework.permissions                         import (
                                                                IsAuthenticated,
                                                                AllowAny
                                                            )
from rest_framework.decorators                          import (
                                                                api_view,
                                                                permission_classes,
)
from rest_framework.response                            import  Response
from django.conf                                        import settings
User                                                    = get_user_model()


'''
Internal use of SessionView
'''
def createNewSessionRecord(theUser, session, info) -> RefreshToken:

    # In This particular function, by receiving user and session type info as input parameters
    # AuthenticationSession objects will be made and return refresh and access casted to string plus a session_id
    # to where ever asked for
    newSession                                          = AuthenticationSession.objects.create(user = theUser, session = session, info = info)
    refresh                                             = RefreshToken.for_user(theUser)
    rightNow                                            = make_aware(datetime.fromtimestamp( refresh['iat'] ))
    newSession.createdAt                                = rightNow

    # Different types of session e.g, LONG and SHORT will cause
    # different initializations according to different expiration option time mentioned in
    # settings.py
    if newSession.session == AuthenticationSession.LONG:
        newSession.expiresAt                            = rightNow + settings.JWT_MULTISESSIONS['LONG_SESSION']['REFRESH_TOKEN_LIFETIME']
        refresh.set_exp(
                                                claim   = "exp", 
                                            from_time   = None, 
                                            lifetime    = settings.JWT_MULTISESSIONS['LONG_SESSION']['REFRESH_TOKEN_LIFETIME'])
    else:
        newSession.expiresAt                            = rightNow + settings.JWT_MULTISESSIONS['SHORT_SESSION']['REFRESH_TOKEN_LIFETIME']
        refresh.set_exp(
                                                claim   = "exp", 
                                            from_time   = None, 
                                            lifetime    = settings.JWT_MULTISESSIONS['SHORT_SESSION']['REFRESH_TOKEN_LIFETIME'])
    
    # access token will be granted by respective to SIMPLE_JWT settings (e.g, "ACCESS_TOKEN_LIFETIME", )
    access                                              = refresh.access_token
    newSession.refresh                                  = str(refresh)
    newSession.session_id                               = slugify(newSession.refresh[-10:]) + '-' + str(newSession.id)
    newSession.save()

    return {
                                            'refresh'   : str(refresh),
                                            'access'    : str(access),
                                        'session_id'    : newSession.session_id
    }

'''
initializeSession is the beginner of the scenario to grant access to the user!
Mandatory inputs: "secret_key", "username_field", "password", "session", "info"
"session" can be either "LONG" or "SHORT". If the request includes "LONG" the duration of the established session stays as long as the mentioned option 
allows in settings.py the same policy applies to "SHORT".
"info" must be mentioned! as specific info e.g., "Chrome 105.0.0.0, OS X 10.15.7 64-bit", "Edge Windows 10", "iOS 16.2" etc.
passing "info" through the API only happes at the session initialization.
This API returns items for successful post requests: 'refresh', 'access' and 'session_id'. 'refresh' and 'access', are the same as the simple_JWT.
'access' is needed for authentication and 'refresh' is needed for getting new 'access' after ex 'access' expiration.
but 'session_id' is a new return item that will be needed for further tasks like listing available sessions or destroying session which needs 'session_id'
'session_id' could/should be saved in the Front-End
'''
# Since intializeSession's Permission class is "AllowAny", "secret_key" should be mentioned in the request post body 
# for security matters! to prevent malicious requests. 
@api_view(['POST'])
@permission_classes([AllowAny])
def initializeSession(request):
    serializer                                          = SessionCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data                                            = serializer.validated_data
        session                                         = data.get('session')
        user                                            = data['user']
        session_key                                     = data['session_key']
        lookups                                         = Q(user = user) & Q(expiresAt__gt=timezone.now()) & Q(session = session)
        availableSessions                               = AuthenticationSession.objects.filter(lookups).order_by('lastUpdateDate')
        canAddNewRefresh                                = True
        canDestroyOldestUpdatedSession                  = settings.JWT_MULTISESSIONS[session_key]['DESTROY_OLDEST_ACTIVE_SESSION']
        limitedNumberOfAvailableSessions                = settings.JWT_MULTISESSIONS[session_key]['LIMIT_NUMBER_OF_AVAIL_SESSIONS']
        if (len(availableSessions) >= settings.JWT_MULTISESSIONS[session_key]['MAX_NUMBER_ACTIVE_SESSIONS']):
            canAddNewRefresh                            = False
        
        if not canAddNewRefresh and not canDestroyOldestUpdatedSession and limitedNumberOfAvailableSessions:
            return Response({
                                            "detail"    : "Reached max number of sessions."},                         
                                                status  = status.HTTP_400_BAD_REQUEST)
        elif not canAddNewRefresh and canDestroyOldestUpdatedSession and limitedNumberOfAvailableSessions:
            numberOfSessionsToBeDeleted                 = abs(len(availableSessions) - settings.JWT_MULTISESSIONS[session_key]['MAX_NUMBER_ACTIVE_SESSIONS'])
            for i, item in enumerate(availableSessions):
                if i <= numberOfSessionsToBeDeleted:
                    item.delete()
        
        keys                                            = createNewSessionRecord(user, session, data.get('info'))
        return Response({
                                            'refresh'   : keys['refresh'],
                                            'access'    : keys['access'],
                                        'session_id'    : keys['session_id'],},
                                                status  = status.HTTP_200_OK)
    return Response({
                                            "detail"    : "No active account found with the given credentials"},                         
                                                status  = status.HTTP_401_UNAUTHORIZED)
'''
To refresh The Access token after expiration, a post request must be called through refreshSession API.
Mandatory inputs: "secret_key", "session", "refresh"
"session" can be either "LONG" or "SHORT" BUT the session must be the same as The initialized session which yields the refresh. 
Otherwise, the session including the correct 'refresh' will be deleted.
Since the "refreshSession" permission class is "AllowAny", to prevent malicious requests "secret_key" must be mentioned in the request post body.
'''
@api_view(['POST'])
@permission_classes([AllowAny])
def refreshSession(request):
    serializer                                          = SessionRefresh(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data                                            = serializer.validated_data
        refresh_token                                   = data.get('refresh')
        
        lookups                                         = Q(refresh=refresh_token)
        qs                                              = AuthenticationSession.objects.filter(lookups)
        if qs.exists():
            sessionObj                                  = qs.first()
            updatedRefresh                              = False

            new_RefreshToken                            = None
            new_access                                  = None

            if sessionObj.expiresAt > timezone.now() and sessionObj.session == data.get('session'):

                sessionType_KEY                         = data.get('session_key')
                
                try:

                    # Retrive the token from JWT Model!
                    theOldRefreshToken                  = RefreshToken(refresh_token)
                    theUserId                           = theOldRefreshToken["user_id"]
                    theUser                             = User.objects.get(Q(id=theUserId))

                    if settings.JWT_MULTISESSIONS[sessionType_KEY]['ROTATE_REFRESH_TOKENS']:
                        new_RefreshToken                = RefreshToken.for_user(theUser)
                        updatedRefresh                  = True
                        if settings.JWT_MULTISESSIONS[sessionType_KEY]['BLACKLIST_AFTER_ROTATION']:
                            theOldRefreshToken.blacklist()
                            updatedRefresh              = True

                    else:
                        new_RefreshToken                = theOldRefreshToken
                        if settings.JWT_MULTISESSIONS[sessionType_KEY]['UPDATE_LAST_LOGIN']:
                            new_RefreshToken.set_iat(
                                                claim   = 'iat', 
                                                at_time = timezone.now())
                            # check if updateRefresh flag should chnage!

                    rightNow                            = make_aware(datetime.fromtimestamp(new_RefreshToken['iat']))
                    if settings.JWT_MULTISESSIONS[sessionType_KEY]['UPDATE_LAST_LOGIN']:
                        sessionObj.lastUpdateDate       = rightNow
                        
                    if settings.JWT_MULTISESSIONS[sessionType_KEY]['EXTEND_SESSION'] and \
                        (settings.JWT_MULTISESSIONS[sessionType_KEY]['EXTEND_SESSION_EVERY_TIME'] or 
                        sessionObj.expiresAt < timezone.now() + settings.JWT_MULTISESSIONS[sessionType_KEY]['EXTEND_SESSION_ONCE_AFTER_EACH']):
                        # If The update each time flag is true then should rotate refresh 
                        # Or Rotate Refresh after each amount of time 
                        sessionObj.expiresAt            = rightNow + settings.JWT_MULTISESSIONS[sessionType_KEY]['REFRESH_TOKEN_LIFETIME']
                        updatedRefresh                  = True
                        new_RefreshToken.set_exp(
                                                claim   = "exp",
                                            from_time   = None,
                                            lifetime    = settings.JWT_MULTISESSIONS[sessionType_KEY]['REFRESH_TOKEN_LIFETIME']
                                        )

                    else:
                        # Won't update refresh
                        pass
                    new_access                          = new_RefreshToken.access_token
                    
                except Exception as e:
                    return Response({
                                            "detail"    : "No active account found with the given credentials! Or Haven't set rest_framework_simplejwt.token_blacklist in settings.INSTALLED_APPS"},                         
                                                status  = status.HTTP_401_UNAUTHORIZED) 

                if updatedRefresh:
                    sessionObj.refresh                  = str(new_RefreshToken)
                sessionObj.save()
                if updatedRefresh:
                    return Response({
                                            "refresh"   : str(new_RefreshToken),
                                                "access": str(new_access)
                                    } ,
                                                status  = status.HTTP_200_OK)
                return Response({
                                                "access": str(new_access)
                                } ,
                                                status  = status.HTTP_200_OK)

            else:
                # it's expired or not honest request because of difference between saved and requested session
                # by the way remember to add new feature like browser or request system info
                try: 
                    token                               = RefreshToken(refresh_token)
                    token.blacklist()
                    sessionObj.delete()
                        
                except Exception as e:
                    return Response({
                                            "detail"    : "Perhaps Haven't set rest_framework_simplejwt.token_blacklist in settings.INSTALLED_APPS",                         
                                    },         status   = status.HTTP_400_BAD_REQUEST)

                return Response({
                                            "detail"    : "Token is invalid or expired",
                                                "code"  : "token_not_valid"},                         
                                                status  = status.HTTP_401_UNAUTHORIZED)

    return Response({
                                            "detail"    : "No active account found with the given credentials"},                         
                                                status  = status.HTTP_401_UNAUTHORIZED)

'''
 This post API will return a list of all active sessions
 Mandatory input: "session"
 "session" can be either "LONG" or "SHORT" or "ALL" 
 If The requested session is "LONG" then The Return List will contain only "LONG" sessions Info.
 If The requested session is "SHORT" then The Return List will contain only "SHORT" sessions Info.
 If The requested session is "ALL" then The Return List will contain both "SHORT" and "LONG" sessions Info. 
 Since listOfActiveSessions' Permission class is "IsAuthenticated", There's no need for "secret_key" because The Access 
 credential attached to the request is needed by default.
'''
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def listOfActiveSessions(request):
    serializer                                          = ListRequestSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data                                            = serializer.validated_data
        session                                         = data.get('session')
        
        lookups                                         = Q(user = request.user) & Q(expiresAt__gt=timezone.now())
        if not data.get('all'):
            lookups                                     = Q(user = request.user) & Q(expiresAt__gt=timezone.now()) & Q(session = session)

        qs                                              = AuthenticationSession.objects.filter(lookups)
        dictionaryOfSessions                            = data.get('dictionaryOfSessions')
        sessionCaptions                                 = {
                                                            AuthenticationSession.SHORT:    "Short",
                                                            AuthenticationSession.LONG:     "Long"
                                                        }
        if qs.exists():
            for eachSession in qs:
                dictionaryOfSessions[sessionCaptions[eachSession.session]]["Sessions"].append({
                                                                                                "session_id"    : eachSession.session_id,
                                                                                                "created_at"    : eachSession.createdAt,
                                                                                                "last_update"   : eachSession.lastUpdateDate,
                                                                                                "expires_at"    : eachSession.expiresAt,
                                                                                                "session_info"  : eachSession.info,
                                                                                                                })
                dictionaryOfSessions[sessionCaptions[eachSession.session]]["Available Sessions"]                += 1

            if sessionCaptions[AuthenticationSession.SHORT] in dictionaryOfSessions: 
                if settings.JWT_MULTISESSIONS["SHORT_SESSION"]["LIMIT_NUMBER_OF_AVAIL_SESSIONS"]:
                    dictionaryOfSessions[sessionCaptions[AuthenticationSession.SHORT]]["Available Sessions"]    = str(abs(settings.JWT_MULTISESSIONS["SHORT_SESSION"]["MAX_NUMBER_ACTIVE_SESSIONS"] - dictionaryOfSessions[sessionCaptions[AuthenticationSession.SHORT]]["Available Sessions"]))
                else: 
                    dictionaryOfSessions[sessionCaptions[eachSession.session]]["Available Sessions"]            = "Unlimited"

            if sessionCaptions[AuthenticationSession.LONG]in dictionaryOfSessions: 
                if settings.JWT_MULTISESSIONS["LONG_SESSION"]["LIMIT_NUMBER_OF_AVAIL_SESSIONS"]:
                    dictionaryOfSessions[sessionCaptions[AuthenticationSession.LONG]]["Available Sessions"]    = str(abs(settings.JWT_MULTISESSIONS["LONG_SESSION"]["MAX_NUMBER_ACTIVE_SESSIONS"] - dictionaryOfSessions[sessionCaptions[AuthenticationSession.LONG]]["Available Sessions"]))
                else: 
                    dictionaryOfSessions[sessionCaptions[AuthenticationSession.LONG]]["Available Sessions"]    = "Unlimited"

        return Response(                                dictionaryOfSessions,
                                                status  = status.HTTP_200_OK)

    return Response({
                                            "detail"    : "No active account found with the given credentials"},                         
                                                status  = status.HTTP_401_UNAUTHORIZED)
'''
 This post API will destroy sessions by their 'session_id' if the mentioned 'session_id' belonged to the user who did make the request.
 Mandatory input: "session_id"
 Since destroySessionById' Permission class is "IsAuthenticated", There's no need for "secret_key" because The Access 
 credential attached to the request is needed by default.
'''
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def destroySessionById(request):
    serializer                                          = DestroySessionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data                                            = serializer.validated_data
        
        lookups                                         = Q(user = request.user) & Q(session_id = data.get("session_id")) 
        qs                                              = AuthenticationSession.objects.filter(lookups)
        if qs.exists():
            qs                                          = qs.first()
            
            try:
                refresh_token                           = qs.refresh
                token                                   = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response({
                                            "detail"    : "Perhaps Haven't set rest_framework_simplejwt.token_blacklist in settings.INSTALLED_APPS",                         
                                },             status   = status.HTTP_400_BAD_REQUEST)
            
            qs.delete()
            
            return Response({},                 status  = status.HTTP_200_OK)

    return Response({
                                            "detail"    : "No active account found with the given credentials"},                         
                                                status  = status.HTTP_401_UNAUTHORIZED)
'''
 This post API will destroy all other sessions except mentioned "refresh" session.
 Mandatory input: "refresh", "session"
 "session" legal choices are: "SHORT", "LONG", "ALL"
 If "session" is "LONG" the API will remove all available "LONG" sessions except mentioned "refresh".
 If "session" is "SHORT" the API will remove all available "SHORT" sessions except mentioned "refresh".
 If "session" is "ALL" the API will remove all available sessions without considering what type of session 
 is about to be removed except the mentioned "refresh" session.
 Since destroyAllOtherSessions' Permission class is "IsAuthenticated", There's no need for "secret_key" because The Access 
 credential attached to the request is needed by default.
'''
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def destroyAllOtherSessions(request):
    serializer                                          = DestroyAllOtherSessionsSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data                                            = serializer.validated_data
        
        lookups                                         = Q(user = request.user)
        if data['session']                              in [0, 1]:
            lookups                                     = Q(user = request.user) & Q(session = data.get('session'))
        qs                                              = AuthenticationSession.objects.filter(lookups)
        if qs.exists():
            for each in qs:
                if each.refresh                         == data.get('refresh'):
                    continue
                try:
                    refresh_token                       = each.refresh
                    token                               = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as e:
                    return Response({
                                            "detail"    : "Perhaps Haven't set rest_framework_simplejwt.token_blacklist in settings.INSTALLED_APPS",                         
                                    },         status   = status.HTTP_400_BAD_REQUEST)
                each.delete()
            return Response({},                 status  = status.HTTP_200_OK)
    return Response({
                                            "detail"    : "No active account found with the given credentials"},                         
                                                status  = status.HTTP_401_UNAUTHORIZED)
'''
 This post API will logout the session assigned to the mentioned 'refresh'
 Mandatory input: "refresh", "secret_key"
 Since the logout Permission class is "AllowAny", to prevent malicious requests "secret_key" must be mentioned in the request post body.
'''
@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    serializer                                          = LogoutSessionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data                                            = serializer.validated_data
        
        lookups                                         = Q(refresh = data.get('refresh'))
        qs                                              = AuthenticationSession.objects.filter(lookups)
        if qs.exists():
            qs                                          = qs.first()
            
            try:
                refresh_token                           = qs.refresh
                token                                   = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response({
                                            "detail"    : "Perhaps Haven't set rest_framework_simplejwt.token_blacklist in settings.INSTALLED_APPS",                         
                                },             status   = status.HTTP_400_BAD_REQUEST)
            
            qs.delete()
            
            return Response({},                 status  = status.HTTP_200_OK)

    return Response({
                                            "detail"    : "No active account found with the given credentials"},                         
                                                status  = status.HTTP_401_UNAUTHORIZED)

