from django.contrib import admin


from django.contrib import admin
from .models import AuthenticationSession


@admin.register(AuthenticationSession)
class SessionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'expiresAt',
    )

    list_filter = ('user', 'expiresAt')
    readonly_fields = ('session_id', 'session', 'user', 'info',  'expiresAt', 'refresh', 'createdAt', 'lastUpdateDate', )

    # def has_delete_permission(self, request, obj=None):
    #     return False

    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False