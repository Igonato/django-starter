"""URL Configuration for authentication and user management"""

from django.urls import include, path

from .views import auth, callback, oauth, provider

urlpatterns = [
    path('api/auth/browsable/', include('rest_framework.urls')),
    path('api/auth/', include('rest_registration.api.urls')),
    path('api/auth/', auth, name='auth-root'),
    path('api/auth/oauth/', oauth, name='oauth'),
    path(
        'api/auth/oauth/provider/<str:provider>/',
        provider,
        name='oauth-provider'
    ),
    path(
        'api/auth/oauth/callback/<str:provider>/',
        callback,
        name='oauth-callback'
    ),
]
