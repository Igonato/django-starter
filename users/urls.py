"""URL Configuration for authentication and user management"""

from django.urls import include, path

from .views import auth

urlpatterns = [
    path('api/auth/browsable/', include('rest_framework.urls')),
    path('api/auth/', include('rest_registration.api.urls')),
    path('api/auth/', auth, name='auth-root'),
]
