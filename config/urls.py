"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from importlib.util import find_spec

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

from .views import home

urlpatterns = [
    path('', RedirectView.as_view(url='api/'), name='index'),
    path('admin/', admin.site.urls),
    path('api/', home, name='api-root'),
]

# Automatically add urls form urls.py for installed project apps
for app in apps.get_app_configs():
    if str(settings.BASE_DIR) not in app.path:
        continue

    module = app.name + '.urls'
    if find_spec(module) is not None and module != __name__:
        urlpatterns += [path('', include(module))]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
