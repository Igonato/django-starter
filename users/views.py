from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth(request, format=None):
    """Authentication and authorization related endpoints:"""
    return Response({
        name.split(':')[-1]: reverse(name, request=request)
        for name in [
            'rest_registration:change-password',
            'rest_registration:login',
            'rest_registration:logout',
            'rest_registration:profile',
            'rest_registration:register',
            'rest_registration:register-email',
            'rest_registration:reset-password',
            'rest_registration:send-reset-password-link',
            'rest_registration:verify-email',
            'rest_registration:verify-registration',
        ]
    })
