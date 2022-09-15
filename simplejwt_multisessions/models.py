
'''

Created By Benyamin Agha Ebrahimi, 10 Aug 2022

'''
from django.db                                      import models
from django.conf                                    import settings
User                                                = settings.AUTH_USER_MODEL


class AuthenticationSession(models.Model):

    session_id                                      = models.SlugField(max_length=510, unique=True)
    # It's known as the businesses type which is short type of session and is about to expires after 24hr
    SHORT                                           = 0
    # Also Known as the mobile/customer/app type which is long type of session and is about to expires after 30 days and
    # if the user tries to access through the current session after end of the halftime of the lifetime the session's expiration date will
    # be extented to it's next 30 days!
    LONG                                            = 1 

    SESSION_TYPE                                    = (
                                                        (SHORT , 'short'),
                                                        (LONG  , 'long'),
    )
    session                                         = models.IntegerField(choices=SESSION_TYPE, default=SHORT )
    user                                            = models.ForeignKey(User, related_name='user_sessions', on_delete = models.CASCADE)

    refresh                                         = models.CharField(max_length=510)
    # access                                          = models.CharField(max_length=510)

    expiresAt                                       = models.DateTimeField(blank = True, null = True)
    
    createdAt                                       = models.DateTimeField(auto_now_add=True)
    lastUpdateDate                                  = models.DateTimeField(auto_now_add=True)
    # updatedSessionTime                              = models.DateTimeField(auto_now_add=True)

    info                                            = models.TextField(blank = True, null = True)        

    def get_lastUpdateDate(self):
        return self.lastUpdateDate

    # def __str__(self):
    #     return self.token