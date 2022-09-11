
'''
Created By Benyamin, 14 Aug 2022
'''
from django.contrib.auth                                import get_user_model
from django.test                                        import TestCase
from django.urls                                        import reverse
from rest_framework                                     import status
from rest_framework.test                                import APIClient
from django.db.models                                   import Q
from .models                                            import AuthenticationSession
from django.utils                                       import timezone
from datetime                                           import timedelta
from rest_framework_simplejwt.tokens                    import RefreshToken
from rest_framework_simplejwt.token_blacklist.models    import BlacklistedToken
from django.conf                                        import settings
User = get_user_model()

user_create_url                             = '/api/accounts/create/'
user_url                                    = '/api/accounts/user/'
request_verify_sms                          = '/api/accounts/request_verify_sms/'

theKey                                      = settings.SECRET_KEY

class UserTestCase(TestCase):

    def __settings(self):
        settings.JWT_MULTISESSIONS           = {
            'SECRET': theKey,
            'LONG_SESSION':{
                'REFRESH_TOKEN_LIFETIME': timedelta(days= 30),
                
                'ROTATE_REFRESH_TOKENS': False,
                'UPDATE_LAST_LOGIN': False,
                'BLACKLIST_AFTER_ROTATION': False,

                'EXTEND_SESSION': True,
                'EXTEND_SESSION_EVERY_TIME': False,
                'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(days= 15),
                
                'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
                'MAX_NUMBER_ACTIVE_SESSIONS': 5,
                'DESTROY_OLDEST_ACTIVE_SESSION': True,
            }, 
            'SHORT_SESSION': {
                'REFRESH_TOKEN_LIFETIME': timedelta(days= 1),
                
                'ROTATE_REFRESH_TOKENS': False,
                'UPDATE_LAST_LOGIN': True,
                'BLACKLIST_AFTER_ROTATION': True,
                
                'EXTEND_SESSION': False,
                'EXTEND_SESSION_EVERY_TIME': False,
                'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(hours= 12),
                
                'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
                'MAX_NUMBER_ACTIVE_SESSIONS': 1,
                'DESTROY_OLDEST_ACTIVE_SESSION': True,
            }
        }
 
    def __setupBasicUser(self): 
        self.username = 'testuser'
        self.password = 'somepassword'
        self.user = User.objects.create_user(username= self.username, password=self.password)
        # login = self.client.login(username='testuser', password='12345')

        # self.oldPassword = 'somepassword'
        # self.user = User.objects.create_user(
        #     cellphone='09128136105', 
        #     password = self.oldPassword,
        #     email='mohammadreza.khp@KHP.com',
        #     # full_name = 'Mohammadreza khosrow-pour',
        #     first_name = 'Mohammadreza',
        #     last_name = 'khosrow-pour',  'cellphone': self.user.cellphone, 'password': self.oldPassword
        #     'username': self.username, 'password': self.password
        #     )
        



    

    def setUp(self):
        self.__settings()
        self.__setupBasicUser()
        # self.__setupSupervisorUser()

        self.count_of_users     = User.objects.all().count()


    def get_client_with_authentication(self, access):

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + access)
        return client

    def test_get_authentication(self):
        # try to access the user tokens with some missed keys
        url = reverse('initialize_session')
        resp = self.client.post(url, {'username': self.username, 'password': self.password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        hasSecret_key = 'secret_key' in resp.json()
        hasSession = 'session' in resp.json()
        self.assertTrue(hasSecret_key)
        self.assertTrue(hasSession)
        
        # With short session in request e.g. session=0
        # try to access the user with correct keys and check if are 'refresh' and 'access' tokens available in return json
        resp = self.client.post(url, {'username': self.username, 'password': self.password, 'session': "SHORT", 'secret_key': theKey}, format='json')
        hasInfo = 'info' in resp.json()
        self.assertTrue(hasInfo)
        resp = self.client.post(url, {'username': self.username, 'password': self.password, 'session': "SHORT", 'secret_key': theKey, 'info': "Test"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        hasRefresh = 'refresh' in resp.json()
        hasAccess = 'access' in resp.json()
        self.assertTrue(hasRefresh)
        self.assertTrue(hasAccess)
        refresh_s_0 = resp.json()['refresh']
        # access_s_0 = resp.json()['access']

        # With long session in request e.g. session=1
        # try to access the user with correct keys and check if are 'refresh' and 'access' tokens available in return json
        resp = self.client.post(url, {'username': self.username, 'password': self.password, 'session': "LONG", 'secret_key': theKey, 'info': "Test"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        hasRefresh = 'refresh' in resp.json()
        hasAccess = 'access' in resp.json()
        self.assertTrue(hasRefresh)
        self.assertTrue(hasAccess)
        refresh_s_1 = resp.json()['refresh']
        self.assertNotEqual(refresh_s_0, refresh_s_1)

        # check if the two requested sessions are made in db!
        countOfSession = AuthenticationSession.objects.all()
        self.assertEqual(len(countOfSession), 2)

        # check if Authentication session is made with correct session type
        e1 = AuthenticationSession.objects.all()[0].expiresAt
        diff1 = abs(e1 - (timezone.now() + settings.JWT_MULTISESSIONS['SHORT_SESSION']['REFRESH_TOKEN_LIFETIME'] - timedelta(seconds = 60)))
        self.assertTrue(diff1 < timedelta(seconds = 60))

        e2 = AuthenticationSession.objects.all()[1].expiresAt
        diff2 = abs(e2 - (timezone.now() + settings.JWT_MULTISESSIONS['LONG_SESSION']['REFRESH_TOKEN_LIFETIME'] - timedelta(seconds = 60)))
        self.assertTrue(diff2 < timedelta(seconds = 60))

        e3 = e2-e1
        diff3 = abs(e3 - (settings.JWT_MULTISESSIONS['LONG_SESSION']['REFRESH_TOKEN_LIFETIME'] - settings.JWT_MULTISESSIONS['SHORT_SESSION']['REFRESH_TOKEN_LIFETIME']))
        self.assertTrue(diff3 < timedelta(seconds = 60))

        numberOfValidAuthenticationSession = len(AuthenticationSession.objects.all())
        self.assertEqual(numberOfValidAuthenticationSession, 2)

    def test_limitated_numberOfShort_sessions(self):
        # Establish Property of the test!
        s_type = 'SHORT'
        s_key = 'SHORT_SESSION'
        info_text = 'test_limitated_numberOfShort_sessions'
        # Set first test values!
        settings.JWT_MULTISESSIONS[s_key] = {
                'REFRESH_TOKEN_LIFETIME': timedelta(days= 1),
                
                'ROTATE_REFRESH_TOKENS': False,
                'UPDATE_LAST_LOGIN': False,
                'BLACKLIST_AFTER_ROTATION': False,
                
                'EXTEND_SESSION': False,
                'EXTEND_SESSION_EVERY_TIME': False,
                'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(hours= 12),
                
                'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
                'MAX_NUMBER_ACTIVE_SESSIONS': 2,
                'DESTROY_OLDEST_ACTIVE_SESSION': False,
            }
        url = reverse('initialize_session')
        resp_1 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertTrue('refresh' in resp_1.json())
        r1 = resp_1.json()['refresh']
        
        resp_2 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertTrue('refresh' in resp_2.json())
        r2 = resp_2.json()['refresh']
        
        resp_3 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertEqual(resp_3.status_code , status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp_3.json()['detail'], 'Reached max number of sessions.')
        self.assertFalse('refresh' in resp_3.json())

        sessions = AuthenticationSession.objects.filter(Q(refresh=r1) | Q(refresh=r2))
        self.assertEqual(len(sessions), 2)

        settings.JWT_MULTISESSIONS[s_key]['LIMIT_NUMBER_OF_AVAIL_SESSIONS'] = False
        resp_3 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertEqual(resp_3.status_code , status.HTTP_200_OK)
        self.assertTrue('refresh' in resp_3.json())
        r3 = resp_3.json()['refresh']

        resp_4 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertEqual(resp_4.status_code , status.HTTP_200_OK)
        self.assertTrue('refresh' in resp_4.json())
        r4 = resp_4.json()['refresh']

        sessions = AuthenticationSession.objects.filter( Q(refresh=r1) | Q(refresh=r2) | Q(refresh=r3) | Q(refresh=r4) )
        self.assertEqual(len(sessions), 4)

        settings.JWT_MULTISESSIONS[s_key]['LIMIT_NUMBER_OF_AVAIL_SESSIONS'] = True
        settings.JWT_MULTISESSIONS[s_key]['DESTROY_OLDEST_ACTIVE_SESSION'] = True
        
        resp_5 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertEqual(resp_5.status_code , status.HTTP_200_OK)
        self.assertTrue('refresh' in resp_5.json())
        r5 = resp_5.json()['refresh']

        obj = AuthenticationSession.objects.all()
        self.assertEqual(len(obj), 2)
        sessions = AuthenticationSession.objects.filter( Q(refresh=r1) | Q(refresh=r2) | Q(refresh=r3) )
        self.assertEqual(len(sessions), 0)

        sessions = AuthenticationSession.objects.filter(  Q(refresh=r4) | Q(refresh=r5) )
        self.assertEqual(len(sessions), 2)

    def test_limitated_numberOfLong_sessions(self):
        # Establish Property of the test!
        s_type = 'LONG'
        s_key = 'LONG_SESSION'
        info_text = 'test_limitated_numberOfLong_sessions'
        # Set first test values!
        settings.JWT_MULTISESSIONS[s_key] = {
                'REFRESH_TOKEN_LIFETIME': timedelta(days= 30),
                
                'ROTATE_REFRESH_TOKENS': False,
                'UPDATE_LAST_LOGIN': False,
                'BLACKLIST_AFTER_ROTATION': False,
                
                'EXTEND_SESSION': True,
                'EXTEND_SESSION_EVERY_TIME': False,
                'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(days= 15),
                
                'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
                'MAX_NUMBER_ACTIVE_SESSIONS': 2,
                'DESTROY_OLDEST_ACTIVE_SESSION': False,
            }

        url = reverse('initialize_session')
        resp_1 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertTrue('refresh' in resp_1.json())
        r1 = resp_1.json()['refresh']
        
        resp_2 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertTrue('refresh' in resp_2.json())
        r2 = resp_2.json()['refresh']
        
        resp_3 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertEqual(resp_3.status_code , status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp_3.json()['detail'], 'Reached max number of sessions.')
        self.assertFalse('refresh' in resp_3.json())

        sessions = AuthenticationSession.objects.filter(Q(refresh=r1) | Q(refresh=r2))
        self.assertEqual(len(sessions), 2)

        settings.JWT_MULTISESSIONS[s_key]['LIMIT_NUMBER_OF_AVAIL_SESSIONS'] = False
        resp_3 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertEqual(resp_3.status_code , status.HTTP_200_OK)
        self.assertTrue('refresh' in resp_3.json())
        r3 = resp_3.json()['refresh']

        resp_4 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertEqual(resp_4.status_code , status.HTTP_200_OK)
        self.assertTrue('refresh' in resp_4.json())
        r4 = resp_4.json()['refresh']

        sessions = AuthenticationSession.objects.filter( Q(refresh=r1) | Q(refresh=r2) | Q(refresh=r3) | Q(refresh=r4) )
        self.assertEqual(len(sessions), 4)

        settings.JWT_MULTISESSIONS[s_key]['LIMIT_NUMBER_OF_AVAIL_SESSIONS'] = True
        settings.JWT_MULTISESSIONS[s_key]['DESTROY_OLDEST_ACTIVE_SESSION'] = True
        
        resp_5 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertEqual(resp_5.status_code , status.HTTP_200_OK)
        self.assertTrue('refresh' in resp_5.json())
        r5 = resp_5.json()['refresh']

        
        obj = AuthenticationSession.objects.all()
        self.assertEqual(len(obj), 2)
        sessions = AuthenticationSession.objects.filter( Q(refresh=r1) | Q(refresh=r2) | Q(refresh=r3) )
        self.assertEqual(len(sessions), 0)

        sessions = AuthenticationSession.objects.filter(  Q(refresh=r4) | Q(refresh=r5) )
        self.assertEqual(len(sessions), 2)

    def test_get_refresh_SHORT(self):
        # Establish Property of the test!
        s_type = 'SHORT'
        s_key = 'SHORT_SESSION'
        info_text = 'test_get_refresh_SHORT'
        # Set first test values!
        settings.JWT_MULTISESSIONS[s_key] = {
                'REFRESH_TOKEN_LIFETIME': timedelta(days= 1),
                
                'ROTATE_REFRESH_TOKENS': False,
                'UPDATE_LAST_LOGIN': False,
                'BLACKLIST_AFTER_ROTATION': False,
                
                'EXTEND_SESSION': False,
                'EXTEND_SESSION_EVERY_TIME': False,
                'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(hours= 12),
                
                'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
                'MAX_NUMBER_ACTIVE_SESSIONS': 1,
                'DESTROY_OLDEST_ACTIVE_SESSION': True,
            }
        
        # try to refresh without specifying the refresh token!
        url = reverse('refresh_session')
        resp = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST) # Because There's now available refresh token in AuthenticationSession
        self.assertTrue("refresh" in resp.json())
        resp = self.client.post(url, {'username': self.username, 'password': self.password, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST) # Because There's now available refresh token in AuthenticationSession
        self.assertTrue("session" in resp.json())
        resp = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST) # Because There's now available refresh token in AuthenticationSession
        self.assertTrue("secret_key" in resp.json())
        self.assertFalse("info" in resp.json())

        
        url = reverse('initialize_session')
        resp_1 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        refresh_1 = resp_1.json()['refresh']
        exp1_before = AuthenticationSession.objects.get(Q(refresh=refresh_1)).expiresAt
        crd1_before = AuthenticationSession.objects.get(Q(refresh=refresh_1)).createdAt
        self.assertEqual(abs(exp1_before - crd1_before), settings.JWT_MULTISESSIONS[s_key]['REFRESH_TOKEN_LIFETIME'])
        self.assertEqual(info_text,  AuthenticationSession.objects.get(Q(refresh=refresh_1)).info)
        lastUpdate1_before = AuthenticationSession.objects.get(Q(refresh=refresh_1)).lastUpdateDate

        url = reverse('refresh_session')
        # try to access the user tokens with some missed keys
        resp = self.client.post(url, {}, format='json')
        self.assertTrue('refresh' in resp.json())
        self.assertTrue('session' in resp.json())
        self.assertTrue('secret_key' in resp.json())

        # # Checks if with correct session which assigned to first get token call is working properly
        resp = self.client.post(url, {'refresh': refresh_1, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        self.assertEqual(info_text,  AuthenticationSession.objects.get(Q(refresh=refresh_1)).info)
        self.assertEqual(AuthenticationSession.objects.get(Q(refresh=refresh_1)).lastUpdateDate, lastUpdate1_before)

        # by changing default property check if UPDATE_LAST_LOGIN works properly
        settings.JWT_MULTISESSIONS[s_key]['UPDATE_LAST_LOGIN'] = True
        resp = self.client.post(url, {'refresh': refresh_1, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_1))
        self.assertEqual(info_text,  AuthenticationSession.objects.get(Q(refresh=refresh_1)).info)
        self.assertEqual(len(obj), 1)

        # after changing default values of "UPDATE_REFRESH_TOKENS" check if refresh token will be returned!
        lastLogin_1 = AuthenticationSession.objects.get(Q(refresh=refresh_1)).lastUpdateDate
        settings.JWT_MULTISESSIONS[s_key]['ROTATE_REFRESH_TOKENS'] = True
        settings.JWT_MULTISESSIONS[s_key]['UPDATE_LAST_LOGIN'] = False
        resp = self.client.post(url, {'refresh': refresh_1, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertTrue('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        refresh_2 = resp.json().get('refresh')
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_1))
        self.assertEqual(len(obj) , 0)
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_2))
        self.assertEqual(info_text,  obj[0].info)
        self.assertEqual(len(obj), 1)
        self.assertNotEqual(refresh_1, refresh_2)
        lastLogin_2 = AuthenticationSession.objects.get(Q(refresh=refresh_2)).lastUpdateDate
        self.assertEqual(lastLogin_1, lastLogin_2)
        exp1_after = AuthenticationSession.objects.get(Q(refresh=refresh_2)).expiresAt
        self.assertEqual(exp1_before, exp1_after)

        # check for true "BLACLIST_AFTER_ROTATION"
        numberOfBlacklist_before = len(BlacklistedToken.objects.all())
        settings.JWT_MULTISESSIONS[s_key]['BLACKLIST_AFTER_ROTATION'] = True
        resp = self.client.post(url, {'refresh': refresh_2, 'session': s_type, 'secret_key': theKey}, format='json')
        numberOfBlacklist_after_1 = len(BlacklistedToken.objects.all())
        self.assertTrue('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        self.assertEqual(numberOfBlacklist_after_1, numberOfBlacklist_before + 1)
        refresh_3 = resp.json().get('refresh')
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_2))
        self.assertEqual(len(obj) , 0)
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_3))
        self.assertEqual(info_text,  obj[0].info)
        self.assertEqual(len(obj), 1)
        self.assertNotEqual(refresh_2, refresh_3)
        lastLogin_3 = AuthenticationSession.objects.get(Q(refresh=refresh_3)).lastUpdateDate
        self.assertEqual(lastLogin_2, lastLogin_3)
        exp2_after = AuthenticationSession.objects.get(Q(refresh=refresh_3)).expiresAt
        self.assertEqual( exp1_after, exp2_after)

        # resetting properties of "ROTATE_REFRESH_TOKENS" and "UPDATE_LAST_LOGIN" and "BLACKLIST_AFTER_ROTATION"
        settings.JWT_MULTISESSIONS[s_key]['ROTATE_REFRESH_TOKENS'] = False
        settings.JWT_MULTISESSIONS[s_key]['UPDATE_LAST_LOGIN'] = False
        settings.JWT_MULTISESSIONS[s_key]['BLACKLIST_AFTER_ROTATION'] = False
        resp = self.client.post(url, {'refresh': refresh_3, 'session': s_type, 'secret_key': theKey}, format='json')
        numberOfBlacklist_after_2 = len(BlacklistedToken.objects.all())
        self.assertEqual(numberOfBlacklist_after_2, numberOfBlacklist_before + 1)
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_2))
        self.assertEqual(len(obj) , 0)
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_3))
        self.assertEqual(info_text,  obj[0].info)
        self.assertEqual(len(obj), 1)
        lastLogin_3 = AuthenticationSession.objects.get(Q(refresh=refresh_3)).lastUpdateDate
        self.assertEqual(lastLogin_2, lastLogin_3)

        # check if just "EXTEND_SESSION" with true without setting two other flags to true works!
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION'] = True
        resp = self.client.post(url, {'refresh': refresh_3, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())

        # check if just "EXTEND_SESSION_EVERY_TIME" with true without setting "EXTEND_SESSION" flag to true works!
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION'] = False
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION_EVERY_TIME'] = True
        resp = self.client.post(url, {'refresh': refresh_3, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())

        # If every_tiem flag with extend_session set to true works!
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION'] = True
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION_EVERY_TIME'] = True
        resp = self.client.post(url, {'refresh': refresh_3, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertTrue('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        refresh_4 = resp.json()['refresh']
        self.assertNotEqual(refresh_4, refresh_3)
        obj = AuthenticationSession.objects.filter(refresh=refresh_3)
        self.assertEqual(len(obj), 0)

        # Test if once after each time and extend_session set to true, works!
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION'] = True
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION_EVERY_TIME'] = False
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION_ONCE_AFTER_EACH'] = timedelta(hours= 12)
        resp = self.client.post(url, {'refresh': refresh_4, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())

        session = AuthenticationSession.objects.get(refresh= refresh_4)
        session.expiresAt = session.expiresAt - timedelta(hours = 13)
        theRefresh = RefreshToken(session.refresh)
        theRefresh.set_exp(
            claim="exp",
            from_time = None, 
            lifetime = timedelta(hours = 7)
        )
        session.refresh = str(theRefresh)
        expiresAt_before = session.expiresAt
        session.save()

        obj = AuthenticationSession.objects.filter(refresh= refresh_4)
        self.assertEqual(len(obj), 0)
        settings.JWT_MULTISESSIONS[s_key]['REFRESH_TOKEN_LIFETIME'] = timedelta(days= 5)
        resp = self.client.post(url, {'refresh': str(theRefresh), 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertTrue('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        refresh_5 = resp.json()['refresh']
        self.assertNotEqual(refresh_5, str(theRefresh))
        session = AuthenticationSession.objects.get(refresh= refresh_5)
        self.assertLess(expiresAt_before, session.expiresAt)
        settings.JWT_MULTISESSIONS[s_key]['REFRESH_TOKEN_LIFETIME'] = timedelta(days= 1)

        # Test if once after each time and extend_session set to false, works!
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION'] = False
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION_ONCE_AFTER_EACH'] = timedelta(hours= 12)
        resp = self.client.post(url, {'refresh': refresh_5, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())

        session = AuthenticationSession.objects.get(refresh= refresh_5)
        session.expiresAt = session.expiresAt - timedelta(hours = 13)
        theRefresh = RefreshToken(session.refresh)
        theRefresh.set_exp(
            claim="exp",
            from_time = None, 
            lifetime = timedelta(hours = 7)
        )
        session.refresh = str(theRefresh)
        expiresAt_before = session.expiresAt
        session.save()

        obj = AuthenticationSession.objects.filter(refresh= refresh_5)
        self.assertEqual(len(obj), 0)
        settings.JWT_MULTISESSIONS[s_key]['REFRESH_TOKEN_LIFETIME'] = timedelta(days= 5)
        resp = self.client.post(url, {'refresh': str(theRefresh), 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())

        session = AuthenticationSession.objects.get(refresh= theRefresh)
        self.assertEqual(expiresAt_before, session.expiresAt)

    def test_get_refresh_LONG(self):
        # Establish Property of the test!
        s_type = 'LONG'
        s_key = 'LONG_SESSION'
        info_text = 'test_get_refresh_LONG'
        # Set first test values!
        settings.JWT_MULTISESSIONS[s_key] = {
            'REFRESH_TOKEN_LIFETIME': timedelta(days= 30),
        
            'ROTATE_REFRESH_TOKENS': False,
            'UPDATE_LAST_LOGIN': False,
            'BLACKLIST_AFTER_ROTATION': False,

            'EXTEND_SESSION': False,
            'EXTEND_SESSION_EVERY_TIME': False,
            'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(days= 15),
            
            'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
            'MAX_NUMBER_ACTIVE_SESSIONS': 5,
            'DESTROY_OLDEST_ACTIVE_SESSION': True,
            }
        
        # try to refresh without specifying the refresh token!
        url = reverse('refresh_session')
        resp = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST) # Because There's now available refresh token in AuthenticationSession
        self.assertTrue("refresh" in resp.json())
        resp = self.client.post(url, {'username': self.username, 'password': self.password, 'secret_key': theKey, 'info': info_text}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST) # Because There's now available refresh token in AuthenticationSession
        self.assertTrue("session" in resp.json())
        resp = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST) # Because There's now available refresh token in AuthenticationSession
        self.assertTrue("secret_key" in resp.json())
        self.assertFalse("info" in resp.json())

        
        url = reverse('initialize_session')
        resp_1 = self.client.post(url, {'username': self.username, 'password': self.password, 'session': s_type, 'secret_key': theKey, 'info': info_text}, format='json')
        refresh_1 = resp_1.json()['refresh']
        exp1_before = AuthenticationSession.objects.get(Q(refresh=refresh_1)).expiresAt
        crd1_before = AuthenticationSession.objects.get(Q(refresh=refresh_1)).createdAt
        self.assertEqual(abs(exp1_before - crd1_before), settings.JWT_MULTISESSIONS[s_key]['REFRESH_TOKEN_LIFETIME'])
        self.assertEqual(info_text,  AuthenticationSession.objects.get(Q(refresh=refresh_1)).info)
        lastUpdate1_before = AuthenticationSession.objects.get(Q(refresh=refresh_1)).lastUpdateDate

        url = reverse('refresh_session')
        # try to access the user tokens with some missed keys
        resp = self.client.post(url, {}, format='json')
        self.assertTrue('refresh' in resp.json())
        self.assertTrue('session' in resp.json())
        self.assertTrue('secret_key' in resp.json())

        # # Checks if with correct session which assigned to first get token call is working properly
        resp = self.client.post(url, {'refresh': refresh_1, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        self.assertEqual(info_text,  AuthenticationSession.objects.get(Q(refresh=refresh_1)).info)
        self.assertEqual(AuthenticationSession.objects.get(Q(refresh=refresh_1)).lastUpdateDate, lastUpdate1_before)

        # by changing default property check if UPDATE_LAST_LOGIN works properly
        settings.JWT_MULTISESSIONS[s_key]['UPDATE_LAST_LOGIN'] = True
        resp = self.client.post(url, {'refresh': refresh_1, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_1))
        self.assertEqual(info_text,  AuthenticationSession.objects.get(Q(refresh=refresh_1)).info)
        self.assertEqual(len(obj), 1)

        # after changing default values of "UPDATE_REFRESH_TOKENS" check if refresh token will be returned!
        lastLogin_1 = AuthenticationSession.objects.get(Q(refresh=refresh_1)).lastUpdateDate
        settings.JWT_MULTISESSIONS[s_key]['ROTATE_REFRESH_TOKENS'] = True
        settings.JWT_MULTISESSIONS[s_key]['UPDATE_LAST_LOGIN'] = False
        resp = self.client.post(url, {'refresh': refresh_1, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertTrue('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        refresh_2 = resp.json().get('refresh')
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_1))
        self.assertEqual(len(obj) , 0)
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_2))
        self.assertEqual(info_text,  obj[0].info)
        self.assertEqual(len(obj), 1)
        self.assertNotEqual(refresh_1, refresh_2)
        lastLogin_2 = AuthenticationSession.objects.get(Q(refresh=refresh_2)).lastUpdateDate
        self.assertEqual(lastLogin_1, lastLogin_2)
        exp1_after = AuthenticationSession.objects.get(Q(refresh=refresh_2)).expiresAt
        self.assertEqual(exp1_before, exp1_after)

        # check for true "BLACLIST_AFTER_ROTATION"
        numberOfBlacklist_before = len(BlacklistedToken.objects.all())
        settings.JWT_MULTISESSIONS[s_key]['BLACKLIST_AFTER_ROTATION'] = True
        resp = self.client.post(url, {'refresh': refresh_2, 'session': s_type, 'secret_key': theKey}, format='json')
        numberOfBlacklist_after_1 = len(BlacklistedToken.objects.all())
        self.assertTrue('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        self.assertEqual(numberOfBlacklist_after_1, numberOfBlacklist_before + 1)
        refresh_3 = resp.json().get('refresh')
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_2))
        self.assertEqual(len(obj) , 0)
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_3))
        self.assertEqual(info_text,  obj[0].info)
        self.assertEqual(len(obj), 1)
        self.assertNotEqual(refresh_2, refresh_3)
        lastLogin_3 = AuthenticationSession.objects.get(Q(refresh=refresh_3)).lastUpdateDate
        self.assertEqual(lastLogin_2, lastLogin_3)
        exp2_after = AuthenticationSession.objects.get(Q(refresh=refresh_3)).expiresAt
        self.assertEqual( exp1_after, exp2_after)

        # resetting properties of "ROTATE_REFRESH_TOKENS" and "UPDATE_LAST_LOGIN" and "BLACKLIST_AFTER_ROTATION"
        settings.JWT_MULTISESSIONS[s_key]['ROTATE_REFRESH_TOKENS'] = False
        settings.JWT_MULTISESSIONS[s_key]['UPDATE_LAST_LOGIN'] = False
        settings.JWT_MULTISESSIONS[s_key]['BLACKLIST_AFTER_ROTATION'] = False
        resp = self.client.post(url, {'refresh': refresh_3, 'session': s_type, 'secret_key': theKey}, format='json')
        numberOfBlacklist_after_2 = len(BlacklistedToken.objects.all())
        self.assertEqual(numberOfBlacklist_after_2, numberOfBlacklist_before + 1)
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_2))
        self.assertEqual(len(obj) , 0)
        obj = AuthenticationSession.objects.filter(Q(refresh=refresh_3))
        self.assertEqual(info_text,  obj[0].info)
        self.assertEqual(len(obj), 1)
        lastLogin_3 = AuthenticationSession.objects.get(Q(refresh=refresh_3)).lastUpdateDate
        self.assertEqual(lastLogin_2, lastLogin_3)

        # check if just "EXTEND_SESSION" with true without setting two other flags to true works!
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION'] = True
        resp = self.client.post(url, {'refresh': refresh_3, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())

        # check if just "EXTEND_SESSION_EVERY_TIME" with true without setting "EXTEND_SESSION" flag to true works!
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION'] = False
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION_EVERY_TIME'] = True
        resp = self.client.post(url, {'refresh': refresh_3, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())

        # If every_tiem flag with extend_session set to true works!
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION'] = True
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION_EVERY_TIME'] = True
        resp = self.client.post(url, {'refresh': refresh_3, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertTrue('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        refresh_4 = resp.json()['refresh']
        self.assertEqual(refresh_4, refresh_3)
        obj = AuthenticationSession.objects.filter(refresh=refresh_3)
        self.assertEqual(len(obj), 1)

        # Test if once after each time and extend_session set to true, works!
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION'] = True
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION_EVERY_TIME'] = False
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION_ONCE_AFTER_EACH'] = timedelta(days= 15)
        resp = self.client.post(url, {'refresh': refresh_4, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())

        session = AuthenticationSession.objects.get(refresh= refresh_4)
        session.expiresAt = session.expiresAt - timedelta(days = 20)
        theRefresh = RefreshToken(session.refresh)
        theRefresh.set_exp(
            claim="exp",
            from_time = None, 
            lifetime = timedelta(hours = 7)
        )
        session.refresh = str(theRefresh)
        expiresAt_before = session.expiresAt
        session.save()

        obj = AuthenticationSession.objects.filter(refresh= refresh_4)
        self.assertEqual(len(obj), 0)
        settings.JWT_MULTISESSIONS[s_key]['REFRESH_TOKEN_LIFETIME'] = timedelta(days= 30)
        resp = self.client.post(url, {'refresh': str(theRefresh), 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertTrue('refresh' in resp.json())
        self.assertTrue('access' in resp.json())
        refresh_5 = resp.json()['refresh']
        self.assertNotEqual(refresh_5, str(theRefresh))
        session = AuthenticationSession.objects.get(refresh= refresh_5)
        self.assertLess(expiresAt_before, session.expiresAt)
        settings.JWT_MULTISESSIONS[s_key]['REFRESH_TOKEN_LIFETIME'] = timedelta(days= 10)

        # Test if once after each time and extend_session set to false, works!
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION'] = False
        settings.JWT_MULTISESSIONS[s_key]['EXTEND_SESSION_ONCE_AFTER_EACH'] = timedelta(days= 7)
        resp = self.client.post(url, {'refresh': refresh_5, 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())

        session = AuthenticationSession.objects.get(refresh= refresh_5)
        session.expiresAt = session.expiresAt - timedelta(days = 8)
        theRefresh = RefreshToken(session.refresh)
        theRefresh.set_exp(
            claim="exp",
            from_time = None, 
            lifetime = timedelta(hours = 7)
        )
        session.refresh = str(theRefresh)
        expiresAt_before = session.expiresAt
        session.save()

        obj = AuthenticationSession.objects.filter(refresh= refresh_5)
        self.assertEqual(len(obj), 0)
        settings.JWT_MULTISESSIONS[s_key]['REFRESH_TOKEN_LIFETIME'] = timedelta(days= 30)
        resp = self.client.post(url, {'refresh': str(theRefresh), 'session': s_type, 'secret_key': theKey}, format='json')
        self.assertFalse('refresh' in resp.json())
        self.assertTrue('access' in resp.json())

        session = AuthenticationSession.objects.get(refresh= theRefresh)
        self.assertEqual(expiresAt_before, session.expiresAt)
    
    def test_list_of_session(self):
        # Establish Property of the test!
        s_type_long = 'LONG'
        s_key_long = 'LONG_SESSION'
        info_text_long = 'test_limitated_numberOfLong_sessions'
        # Set first test values!
        settings.JWT_MULTISESSIONS[s_key_long] = {
                'REFRESH_TOKEN_LIFETIME': timedelta(days= 30),
                
                'ROTATE_REFRESH_TOKENS': False,
                'UPDATE_LAST_LOGIN': False,
                'BLACKLIST_AFTER_ROTATION': False,
                
                'EXTEND_SESSION': True,
                'EXTEND_SESSION_EVERY_TIME': False,
                'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(days= 15),
                
                'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
                'MAX_NUMBER_ACTIVE_SESSIONS': 2,
                'DESTROY_OLDEST_ACTIVE_SESSION': False,
            }
        # Establish Property of the test!
        s_type_short = 'SHORT'
        s_key_short = 'SHORT_SESSION'
        info_text_short = 'test_limitated_numberOfShort_sessions'
        # Set first test values!
        settings.JWT_MULTISESSIONS[s_key_short] = {
                'REFRESH_TOKEN_LIFETIME': timedelta(days= 1),
                
                'ROTATE_REFRESH_TOKENS': False,
                'UPDATE_LAST_LOGIN': False,
                'BLACKLIST_AFTER_ROTATION': False,
                
                'EXTEND_SESSION': False,
                'EXTEND_SESSION_EVERY_TIME': False,
                'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(hours= 12),
                
                'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
                'MAX_NUMBER_ACTIVE_SESSIONS': 1,
                'DESTROY_OLDEST_ACTIVE_SESSION': False,
            }

        url_initialize_session = reverse('initialize_session')
        resp_long_1 = self.client.post(url_initialize_session, {'username': self.username, 'password': self.password, 'session': s_type_long, 'secret_key': theKey, 'info': info_text_long}, format='json')
        self.assertEqual(resp_long_1.status_code, status.HTTP_200_OK)
        access_long = resp_long_1.json()['access']
        client_long = self.get_client_with_authentication(access_long)

        resp_short_1 = self.client.post(url_initialize_session, {'username': self.username, 'password': self.password, 'session': s_type_short, 'secret_key': theKey, 'info': info_text_short}, format='json')
        self.assertEqual(resp_short_1.status_code, status.HTTP_200_OK)
        access_short = resp_short_1.json()['access']
        client_short = self.get_client_with_authentication(access_short)

        url_list_sessions = reverse('list_sessions')
        resp_list_sessions = self.client.get(url_list_sessions, {}, format='json')
        self.assertEqual(resp_list_sessions.status_code, status.HTTP_401_UNAUTHORIZED)

        response_long = client_long.get(url_list_sessions, data={'format': 'json'}) 
        self.assertEqual(response_long.json()['detail'], 'Method "GET" not allowed.')
        response_short = client_short.get(url_list_sessions, data={'format': 'json'}) 
        self.assertEqual(response_short.json()['detail'], 'Method "GET" not allowed.')

        response_long = client_long.post(url_list_sessions, {} ,format='json') 
        self.assertTrue('session' in response_long.json())
        response_short = client_short.post(url_list_sessions, {} ,format='json') 
        self.assertTrue('session' in response_short.json())

        response_long = client_long.post(url_list_sessions, {'session': 'long'} ,format='json')
        self.assertEqual(response_long.status_code, status.HTTP_200_OK)
        self.assertTrue('Long' in response_long.json()) 
        self.assertTrue('Available Sessions' in response_long.json().get('Long')) 
        self.assertEqual(int(response_long.json()['Long']['Available Sessions']), 1)

        response_long = client_long.post(url_list_sessions, {'session': 'short'} ,format='json')
        self.assertEqual(response_long.status_code, status.HTTP_200_OK)
        self.assertTrue('Short' in response_long.json()) 
        self.assertTrue('Available Sessions' in response_long.json().get('Short')) 
        self.assertEqual(int(response_long.json()['Short']['Available Sessions']), 0)

        response_long = client_long.post(url_list_sessions, {'session': 'all'} ,format='json')
        self.assertEqual(response_long.status_code, status.HTTP_200_OK)
        self.assertTrue('Long' in response_long.json())
        self.assertTrue('Short' in response_long.json())

        
        response_short = client_short.post(url_list_sessions, {'session': 'long'} ,format='json') 
        self.assertEqual(response_short.status_code, status.HTTP_200_OK)
        self.assertTrue('Long' in response_short.json()) 
        self.assertTrue('Available Sessions' in response_short.json().get('Long')) 
        self.assertEqual(int(response_short.json()['Long']['Available Sessions']), 1)

        response_short = client_short.post(url_list_sessions, {'session': 'short'} ,format='json') 
        self.assertEqual(response_short.status_code, status.HTTP_200_OK)
        self.assertTrue('Short' in response_short.json()) 
        self.assertTrue('Available Sessions' in response_short.json().get('Short')) 
        self.assertEqual(int(response_short.json()['Short']['Available Sessions']), 0)

        response_short = client_short.post(url_list_sessions, {'session': 'all'} ,format='json') 
        self.assertEqual(response_short.status_code, status.HTTP_200_OK)
        self.assertTrue('Long' in response_short.json())
        self.assertTrue('Short' in response_short.json())
    
    def test_destroySessionById(self):
        # Establish Property of the test!
        s_type_long = 'LONG'
        s_key_long = 'LONG_SESSION'
        info_text_long = 'test_limitated_numberOfLong_sessions'
        # Set first test values!
        settings.JWT_MULTISESSIONS[s_key_long] = {
                'REFRESH_TOKEN_LIFETIME': timedelta(days= 30),
                
                'ROTATE_REFRESH_TOKENS': False,
                'UPDATE_LAST_LOGIN': False,
                'BLACKLIST_AFTER_ROTATION': False,
                
                'EXTEND_SESSION': True,
                'EXTEND_SESSION_EVERY_TIME': False,
                'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(days= 15),
                
                'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
                'MAX_NUMBER_ACTIVE_SESSIONS': 2,
                'DESTROY_OLDEST_ACTIVE_SESSION': False,
            }
        url_initialize_session = reverse('initialize_session')
        resp_long_1 = self.client.post(url_initialize_session, {'username': self.username, 'password': self.password, 'session': s_type_long, 'secret_key': theKey, 'info': info_text_long}, format='json')
        self.assertEqual(resp_long_1.status_code, status.HTTP_200_OK)
        refresh_1 = resp_long_1.json()['refresh']

        resp_long_2 = self.client.post(url_initialize_session, {'username': self.username, 'password': self.password, 'session': s_type_long, 'secret_key': theKey, 'info': info_text_long}, format='json')
        number_sessions_before_destroy = len(AuthenticationSession.objects.filter(session="1"))
        self.assertEqual(number_sessions_before_destroy, 2)
        sessionId = AuthenticationSession.objects.exclude(refresh=refresh_1)[0].session_id

        url_destorySessionById = reverse('destroy_session_by_id')
        access_long = resp_long_1.json()['access']
        client_long = self.get_client_with_authentication(access_long)
        resp_long = client_long.get(url_destorySessionById, data={'format': 'json'}) 
        self.assertEqual(resp_long.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue('Method "GET" not allowed.' in resp_long.json()['detail'])
        
        resp_long = client_long.post(url_destorySessionById,{}, format='json') 
        self.assertTrue('session_id' in resp_long.json())

        resp_long = client_long.post(url_destorySessionById,{'session_id': sessionId}, format='json') 
        self.assertEqual(resp_long.status_code, status.HTTP_200_OK)
        
        number_sessions_after_destroy = len(AuthenticationSession.objects.filter(session="1"))
        self.assertEqual(number_sessions_after_destroy, 1)
        
        url_list_sessions = reverse('list_sessions')
        resp_long = client_long.post(url_list_sessions,{'session': 'Long'}, format='json') 
        self.assertEqual(int(resp_long.json()['Long']['Available Sessions']), 1)
    
    def test_destroyAllOtherSessions(self):
        # Establish Property of the test!
        s_type_long = 'LONG'
        s_key_long = 'LONG_SESSION'
        # Set first test values!
        settings.JWT_MULTISESSIONS[s_key_long] = {
                'REFRESH_TOKEN_LIFETIME': timedelta(days= 30),
                
                'ROTATE_REFRESH_TOKENS': False,
                'UPDATE_LAST_LOGIN': False,
                'BLACKLIST_AFTER_ROTATION': False,
                
                'EXTEND_SESSION': True,
                'EXTEND_SESSION_EVERY_TIME': False,
                'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(days= 15),
                
                'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
                'MAX_NUMBER_ACTIVE_SESSIONS': 2,
                'DESTROY_OLDEST_ACTIVE_SESSION': False,
            }
        # Establish Property of the test!
        s_type_short = 'SHORT'
        s_key_short = 'SHORT_SESSION'
        info_text_short = 'test_limitated_numberOfShort_sessions'
        # Set first test values!
        settings.JWT_MULTISESSIONS[s_key_short] = {
                'REFRESH_TOKEN_LIFETIME': timedelta(days= 1),
                
                'ROTATE_REFRESH_TOKENS': False,
                'UPDATE_LAST_LOGIN': False,
                'BLACKLIST_AFTER_ROTATION': False,
                
                'EXTEND_SESSION': False,
                'EXTEND_SESSION_EVERY_TIME': False,
                'EXTEND_SESSION_ONCE_AFTER_EACH': timedelta(hours= 12),
                
                'LIMIT_NUMBER_OF_AVAIL_SESSIONS': True,
                'MAX_NUMBER_ACTIVE_SESSIONS': 1,
                'DESTROY_OLDEST_ACTIVE_SESSION': False,
            }

        url_initialize_session = reverse('initialize_session')
        resp_long_1 = self.client.post(url_initialize_session, {'username': self.username, 'password': self.password, 'session': s_type_long, 'secret_key': theKey, 'info': 'long_1'}, format='json')
        access_long = resp_long_1.json()['access']
        client_long = self.get_client_with_authentication(access_long)
        refresh_long_1 = resp_long_1.json()['refresh']
        
        self.client.post(url_initialize_session, {'username': self.username, 'password': self.password, 'session': s_type_long, 'secret_key': theKey, 'info': "long_2"}, format='json')
        self.assertEqual(len(AuthenticationSession.objects.filter(info='long_2')), 1)

        resp_short_1 = self.client.post(url_initialize_session, {'username': self.username, 'password': self.password, 'session': s_type_short, 'secret_key': theKey, 'info': info_text_short}, format='json')
        access_short = resp_short_1.json()['access']
        client_short = self.get_client_with_authentication(access_short)
        refresh_short_1 = resp_short_1.json()['refresh']

        self.assertEqual(len(AuthenticationSession.objects.all()), 3)

        url_destory_other = reverse('destory_all_other')
        resp_destory = client_long.post(url_destory_other,{'refresh': refresh_long_1, 'session': 'long'},  format='json') 
        self.assertEqual(resp_destory.status_code, status.HTTP_200_OK)

        self.assertEqual(len(AuthenticationSession.objects.all()), 2)
        self.assertEqual(len(AuthenticationSession.objects.filter(info='long_2')), 0)

        self.client.post(url_initialize_session, {'username': self.username, 'password': self.password, 'session': s_type_long, 'secret_key': theKey, 'info': "long_2"}, format='json')

        resp_destory = client_short.post(url_destory_other,{'refresh': refresh_short_1, 'session': 'all'},  format='json') 
        self.assertEqual(resp_destory.status_code, status.HTTP_200_OK)
        self.assertEqual(len(AuthenticationSession.objects.all()), 1)
        self.assertEqual(len(AuthenticationSession.objects.filter(session = 1)), 0)

    def test_logout(self):
        # Establish Property of the test!
        s_type_long = 'LONG'
        s_key_long = 'LONG_SESSION'
        # Establish Property of the test!
        s_type_short = 'SHORT'
        s_key_short = 'SHORT_SESSION'
        info_text_short = 'test_limitated_numberOfShort_sessions'
        # Set first test values!

        url_initialize_session = reverse('initialize_session')
        resp_long_1 = self.client.post(url_initialize_session, {'username': self.username, 'password': self.password, 'session': s_type_long, 'secret_key': theKey, 'info': s_key_long}, format='json')
        refresh_long_1 = resp_long_1.json()['refresh']
        self.assertEqual(len(AuthenticationSession.objects.filter(refresh=refresh_long_1)), 1)

        self.assertEqual(len(AuthenticationSession.objects.filter(info=s_key_long)), 1)

        resp_short_1 = self.client.post(url_initialize_session, {'username': self.username, 'password': self.password, 'session': s_type_short, 'secret_key': theKey, 'info': s_key_short}, format='json')
        refresh_short_1 = resp_short_1.json()['refresh']
        self.assertEqual(len(AuthenticationSession.objects.filter(refresh=refresh_short_1)), 1)

        url_logout = reverse('logout')
        resp = self.client.get(url_logout, data={'format': 'json'}) 
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue('detail' in resp.json())

        resp = self.client.post(url_logout, {}, format='json')
        self.assertTrue('secret_key' in resp.json())
        self.assertTrue('refresh' in resp.json())

        resp = self.client.post(url_logout, {'secret_key': theKey, 'refresh': refresh_long_1}, format='json')
        self.assertEqual(len(AuthenticationSession.objects.filter(session = 1 )) , 0)
        
        resp = self.client.post(url_logout, {'secret_key': theKey, 'refresh': refresh_short_1}, format='json')
        self.assertEqual(len(AuthenticationSession.objects.filter(session = 0 )) , 0)

        self.assertEqual(len(AuthenticationSession.objects.all()), 0)