"""URL Configuration for Authentication and User management"""

from django.urls import include, path

urlpatterns = [
    path('api/auth/browsable/', include('rest_framework.urls')),
    path('api/auth/', include('rest_registration.api.urls')),
]
