"""
Django settings for the project.

Created using https://github.com/Igonato/django-starter template.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import os
import re
from ast import literal_eval
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Tooling for using environment variables as settings

def env(name, default='__undefined__', parse=lambda x: x, _g=globals()):
    """
    Get an environment variable by the name, parse and add it to the
    module namespace, which allows you to use:

        env('SETTING_NAME')

    instead of:

        SETTING_NAME = env('SETTING_NAME')

    which helps with long names and preventing typos. You can still use
    the second version if you like it, or if you want to have a
    different name for the environment variable and the setting i.e.:

        SETTING_NAME = env('DJANGO_SETTING_NAME')

    Tip: add a `print(name)` statement to see every var in use and then
    check the list against your production environment to ensure that
    you didn't forget any settings used by your app.

    >>> os.environ.update({
    ...     'A': 'test',
    ...     'B': ' "test" ',
    ...     'C': '42',
    ... })
    >>> env('A', _g=globals())
    'test'
    >>> A
    'test'
    >>> env('B')
    'test'
    >>> env('C', parse=int)
    42
    >>> env('D')
    Traceback (most recent call last):
        ...
    django.core.exceptions.ImproperlyConfigured: D must be set
    >>> env('D', 'default')
    'default'
    >>> env('D', None) is None  # None works as a default
    True
    """
    try:
        _g[name] = parse(unquote(os.environ[name].strip()))
    except KeyError as e:
        if default == '__undefined__':
            raise ImproperlyConfigured(f"{name} must be set") from e
        _g[name] = default
    return _g[name]


def unquote(s):
    """
    Remove a *matching* set of quotes from a string if present:

    >>> unquote('Never')
    'Never'
    >>> unquote('"Gonna"')
    'Gonna'
    >>> unquote("'Give'")
    'Give'
    >>> unquote('You"')
    'You"'
    >>> unquote('\\'Up"')
    '\\'Up"'
    """
    if re.match(r'^([\"\']).*(\1)$', s):
        return s[1:-1]
    return s


def must_be_explicitly_false(truthy_env_var):
    """
    Parse a string into a boolean with a bias towards truthfulness:

    >>> must_be_explicitly_false("FALSE")
    False
    >>> must_be_explicitly_false("")
    True
    >>> must_be_explicitly_false("0")
    True
    """
    return truthy_env_var.lower() not in ['false', 'no', 'n']


def must_be_explicitly_true(falsy_env_var):
    """
    Parse a string into a boolean with a bias towards falseness:

    >>> must_be_explicitly_true("TRUE")
    True
    >>> must_be_explicitly_true("yes")
    True
    >>> must_be_explicitly_true("spam")
    False
    """
    return falsy_env_var.lower() in ['true', 'yes', 'y']


# Security-related settings

# SECURITY WARNING: keep the secret key used in production secret!
env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DJANGO_DEBUG', False, must_be_explicitly_true)

# Example: ALLOWED_HOSTS='example.com 127.0.0.1 [::1]'
env('ALLOWED_HOSTS', [], str.split)

# SSL redirect
env('SECURE_SSL_REDIRECT', True, must_be_explicitly_false)

# Security headers settings
env('SECURE_HSTS_SECONDS', 3600, int)
env('SECURE_HSTS_INCLUDE_SUBDOMAINS', True, must_be_explicitly_false)
env('SECURE_HSTS_PRELOAD', True, must_be_explicitly_false)
env('SECURE_REFERRER_POLICY', 'same-origin')

# Security cookies settings
env('CSRF_COOKIE_SECURE', True, must_be_explicitly_false)
env('SESSION_COOKIE_SECURE', True, must_be_explicitly_false)

# Example: SECURE_PROXY_SSL_HEADER='HTTP_X_FORWARDED_PROTO https'
env('SECURE_PROXY_SSL_HEADER', None, lambda x: tuple(x.split()) or None)

# Example: ADMINS='[("John", "john@example.com")]'
env('ADMINS', [], literal_eval)


# Application definition

INSTALLED_APPS = [
    # Django apps:
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps:
    'django_celery_results',

    # Project apps:
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if env('USE_CACHE_MIDDLEWARE', True, must_be_explicitly_false):
    MIDDLEWARE.insert(1, 'django.middleware.cache.UpdateCacheMiddleware')
    MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')

if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
        'django_extensions',
    ]
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }

ROOT_URLCONF = 'config.urls'

APPEND_SLASH = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': env('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': env('DB_USER', None),
        'PASSWORD': env('DB_PASSWORD', None),
        'HOST': env('DB_HOST', None),
        'PORT': env('DB_PORT', None),
        'CONN_MAX_AGE': env('DB_CONN_MAX_AGE', 0, int),
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/dev/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Cache
# https://docs.djangoproject.com/en/dev/ref/settings/#caches

CACHES = {
    'default': {
        'BACKEND': env(
            'CACHE_BACKEND', 'django.core.cache.backends.locmem.LocMemCache'
        ),
        'LOCATION': env('CACHE_LOCATION', ''),
        'KEY_PREFIX': env('CACHE_KEY_PREFIX', ''),
        'OPTIONS': env('CACHE_OPTIONS', {}, literal_eval),
    }
}

env('CACHE_MIDDLEWARE_SECONDS', 600, int)


# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

env('AUTH_PASSWORD_VALIDATORS', [{
    'NAME': 'django.contrib.auth.password_validation'
            '.UserAttributeSimilarityValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
}], literal_eval)


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

LANGUAGES = [
    ('en', _('English')),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

env('STATIC_URL', '/static/')
env('STATIC_ROOT', BASE_DIR / 'static')

env('MEDIA_URL', '/media/')
env('MEDIA_ROOT', BASE_DIR / 'media')


# Email settings
# https://docs.djangoproject.com/en/dev/topics/email/

env('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
env('EMAIL_HOST', 'localhost')
env('EMAIL_PORT', 25, int)
env('EMAIL_HOST_USER', '')
env('EMAIL_HOST_PASSWORD', '')
env('EMAIL_USE_TLS', True, must_be_explicitly_false)

env('DEFAULT_FROM_EMAIL', 'no-reply@localhost')
env('SERVER_EMAIL', 'root@localhost')


# Logging settings
# https://docs.djangoproject.com/en/dev/topics/logging/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        # Don't log errors about the invalid HTTP_HOST headers.
        # Some environments perform health-checks by poking your
        # webserver at regular intervals using the machine's ip address
        # which spams the error, which will in turn spam your email.
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    }
}

# Custom user model
# https://docs.djangoproject.com/en/dev/topics/auth/customizing/

AUTH_USER_MODEL = 'users.User'

LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'


# Third-party apps settings

# Celery
# https://docs.celeryproject.org/

env('CELERY_BROKER_URL', 'redis://localhost:6379/0')
env('CELERY_RESULT_BACKEND', 'django-db')
