'''

Created By Benyamin Agha Ebrahimi, 10 Aug 2022

'''

from django.contrib.auth                                                import authenticate, get_user_model
from django.conf                                                        import settings
from rest_framework                                                     import serializers

User                                                                    = get_user_model()

class PasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('style', {})

        kwargs['style']['input_type']                                   = 'password'
        kwargs['write_only']                                            = True

        super().__init__(*args, **kwargs)


class SessionCreateSerializer(serializers.Serializer):
    username_field                                                      = User.USERNAME_FIELD
    extra_kwargs                                                        = {
                                                        'secret_key'    : {
                                                            'write_only': True, 
                                                            'required'  : False,
                                                                }
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field]                                = serializers.CharField()
        self.fields['password']                                         = PasswordField()
        self.fields['secret_key']                                       = serializers.CharField()
        self.fields['session']                                          = serializers.CharField()
        self.fields['info']                                             = serializers.CharField()

    def validate(self, data):
        credentials_kwargs                                              = {
                                                    self.username_field : data[self.username_field],
                                                            'password'  : data['password'],
        }
        try:
            credentials_kwargs['request']                               = self.context['request']
        except KeyError:
            pass

        self.user                                                       = authenticate(**credentials_kwargs)
        if not self.user:
            raise serializers.ValidationError("Invalid Credentials or not active account found!")
        if not self.user \
        and data['secret_key']                                          != settings.JWT_MULTISESSIONS['SECRET']:
            raise serializers.ValidationError("Invalid Credentials or not active account found!")
        
        data['user']                                                    = self.user

        if data['secret_key']                                           != settings.JWT_MULTISESSIONS['SECRET']:
            raise serializers.ValidationError("Invalid Credentials !")

        if data['session'].upper()                                      == "LONG":
            data['session']                                             = 1
            data['session_key']                                         = 'LONG_SESSION'
        elif data['session'].upper()                                    == "SHORT":
            data['session']                                             = 0
            data['session_key']                                         = 'SHORT_SESSION'
        else:
            raise serializers.ValidationError("Invalid Session Type. Valid options: ['LONG', 'SHORT']")
        
        return data

class SessionRefresh(serializers.Serializer):
    
    secret_key                                                          = serializers.CharField()
    session                                                             = serializers.CharField()
    refresh                                                             = serializers.CharField()

    extra_kwargs                                                        = {
            'secret_key': {
                'write_only': True, 
                'required': False,
            }
        }
    
    def validate(self, data):
        if data['secret_key']                                           != settings.JWT_MULTISESSIONS['SECRET']:
            raise serializers.ValidationError("Invalid Credentials or not active account found!")

        if data['session'].upper()                                      == "SHORT":
            data['session']                                             = 0
            data['session_key']                                         = 'SHORT_SESSION'
        elif data['session'].upper()                                    == "LONG":
            data['session']                                             = 1
            data['session_key']                                         = 'LONG_SESSION'
        else:
            raise serializers.ValidationError("Invalid Session Type. Valid options: ['LONG', 'SHORT']")

        return data
    


class ListRequestSerializer(serializers.Serializer):
    session                                                             = serializers.CharField()
    def validate(self, data):
        data["dictionaryOfSessions"]                                    = {}
        data['all']                                                     = False

        if data['session'].upper()                                      == "SHORT":
            data['session']                                             = 0
            data["dictionaryOfSessions"]["Short"]                       = {
                                                "Available Sessions"    : 0,
                                                "Sessions"              : [],
                                                }
        elif data['session'].upper()                                    == "LONG":
            data['session']                                             = 1
            data["dictionaryOfSessions"]["Long"]                        = {
                                                "Available Sessions"    : 0,
                                                "Sessions"              : [],
                                                }
        elif data['session'].upper()                                    == "ALL":
            data['session']                                             = 2
            data['all']                                                 = True
            data["dictionaryOfSessions"]["Short"]                       = {
                                                "Available Sessions"    : 0,
                                                "Sessions"              : [],
                                                }
            data["dictionaryOfSessions"]["Long"]                        = {
                                                "Available Sessions"    : 0,
                                                "Sessions"              : [],
                                                }
        else:
            raise serializers.ValidationError("Invalid Session Type. Valid options: ['LONG', 'SHORT', 'ALL']")

        return data
class DestroySessionSerializer(serializers.Serializer):
    session_id                                                          = serializers.CharField()

    extra_kwargs                                                        = {
        'session_id': {
            'write_only': True, 
            'required': False,
        }
    }

class DestroyAllOtherSessionsSerializer(serializers.Serializer):
    refresh                                                             = serializers.CharField()
    session                                                             = serializers.CharField()
    
    extra_kwargs                                                        = {
        'refresh': {
            'write_only': True, 
            'required': False,
        },
        'session': {
            'write_only': True, 
            'required': False,
        }
    }
    def validate(self, data):

        if data['session'].upper()                                      == "SHORT":
            data['session']                                             = 0
            data['caption']                                             = 'Short'
        elif data['session'].upper()                                    == "LONG":
            data['session']                                             = 1
            data['caption']                                             = 'Long'
        elif data['session'].upper()                                    == "ALL":
            data['session']                                             = 2
            data['caption']                                             = 'All'
        else:
            raise serializers.ValidationError("Invalid Session Type")

        return data

class LogoutSessionSerializer(serializers.Serializer):
    
    secret_key                                                          = serializers.CharField()
    refresh                                                             = serializers.CharField()

    extra_kwargs                                                        = {
            'secret_key': {
                'write_only': True, 
                'required': True,
            },
            'refresh': {
                'write_only': True, 
                'required': True,
            }
        }
    
    def validate(self, data):
        if data['secret_key']                                           != settings.JWT_MULTISESSIONS['SECRET']:
            raise serializers.ValidationError("Invalid Credentials or not active account found!")

        return data