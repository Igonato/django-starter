import json
import random
import re
from base64 import b64decode, b64encode
from http import HTTPStatus
from string import ascii_letters, digits
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import login
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.db import IntegrityError, transaction
from django.dispatch import receiver
from django.shortcuts import redirect
from django.utils.translation import gettext as _

import requests
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_registration.signals import user_activated, user_registered

from .models import User


def random_token(length=15, alphabet=ascii_letters + digits):
    """Generate a random string of a specific length"""
    return ''.join(random.choice(alphabet) for i in range(length))


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
            'oauth',
            'rest_registration:profile',
            'rest_registration:register',
            'rest_registration:register-email',
            'rest_registration:reset-password',
            'rest_registration:send-reset-password-link',
            'rest_registration:verify-email',
            'rest_registration:verify-registration',
        ]
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def oauth(request, format=None):
    """OAuth 2.0 URLs for supported providers"""
    return Response({
        provider: reverse('oauth-provider', (provider, ), request=request)
        for provider in settings.OAUTH
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def provider(request, provider, format=None):
    """OAuth 2.0 URLs for supported providers"""
    if provider not in settings.OAUTH:
        raise NotFound(_('Provider %s is not supported.') % provider)

    # If state parameter gets sniffed, it is possible to forge a url
    # that can log user to another OAuth account. We can use Django's
    # TimestampSigner to hash the state value and prevent that
    # Using the signer instead of a hasher to add timestamp
    if 'state_validation' not in request.session:
        request.session['state_validation'] = random_token()

    signer = TimestampSigner()
    signed_validation = signer.sign(request.session['state_validation'])
    state = {
        'signature': signed_validation.split(':', 1)[1],
        'next': request.GET.get('next', None),
    }

    return redirect(settings.OAUTH[provider]['auth_uri'] + '?' + urlencode({
        'response_type': 'code',
        'client_id': settings.OAUTH[provider]['client_id'],
        'redirect_uri': reverse(
            'oauth-callback', (provider, ), request=request
        ),
        'scope': settings.OAUTH[provider]['scope'],
        'state': b64encode(json.dumps(state).encode('utf-8')),
    }))


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def callback(request, provider=None, format=None):
    """
    Callback serving the OAuth redirect uri.

    If the user isn't logged in already, try to log him in based on the
    OAuth user id, if it doesn't exist then a new user is created and
    logged in.

    If the user is logged in already, then we add OAuth info to the
    user's oauth field.
    """
    if provider not in settings.OAUTH:
        raise NotFound(_('Provider %s is not supported.') % provider)

    try:
        state = json.loads(b64decode(request.GET['state']))
        signer = TimestampSigner()
        signer.unsign(
            f'{request.session["state_validation"]}:{state["signature"]}',
            max_age=settings.OAUTH_STATE_MAX_AGE
        )
        del request.session['state_validation']
    except SignatureExpired:
        raise AuthenticationFailed(_('State expired.'))
    except (KeyError, BadSignature):
        raise AuthenticationFailed(_('State is missing or invalid.'))

    code = request.GET.get('code', '')

    # TODO: update to async once Django supports it
    response = requests.post(
        settings.OAUTH[provider]['token_uri'],
        data={
            'code': code,
            'client_id': settings.OAUTH[provider]['client_id'],
            'client_secret': settings.OAUTH[provider]['client_secret'],
            'grant_type': 'authorization_code',
            'redirect_uri': reverse(
                'oauth-callback', (provider, ), request=request
            ),
        },
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
    )

    if response.status_code != HTTPStatus.OK:
        raise AuthenticationFailed(_('OAuth code - token exchange failed.'))

    access_info = response.json()

    if provider == 'google':
        jwt_body = access_info['id_token'].split('.')[1]
        user_info = json.loads(
            b64decode(jwt_body + '=' * (-len(jwt_body) % 4))
        )
        user_id = user_info['sub']
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        email = user_info.get('email', '')
        email_verified = user_info.get('email_verified', False)

    elif provider == 'facebook':
        # TODO: update to async once Django supports it
        response = requests.post(
            'https://graph.facebook.com/me',
            data={'fields': 'first_name,last_name,email'},
            headers={'Authorization': f'Bearer {access_info["access_token"]}'},
        )
        if response.status_code != HTTPStatus.OK:
            raise AuthenticationFailed(
                _('Unable to get user info for OAuth provider %s.') % provider
            )
        user_info = response.json()
        user_id = user_info['id']
        first_name = user_info.get('first_name', '')
        last_name = user_info.get('last_name', '')
        email = user_info.get('email', '')
        email_verified = bool(email)

    else:
        raise AuthenticationFailed(
            _('Unable to get user info for OAuth provider %s.') % provider
        )

    if request.user.is_anonymous:
        try:
            user = User.objects.get(
                **{f'oauth__{provider}__{user_id}__has_keys': ['access_info']}
            )
        except User.DoesNotExist:
            user = User(
                username='user' + random_token(7, digits),
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_verified=email_verified,
                oauth={},
            )
            user.set_unusable_password()

            # There is a small chance that the random username we just
            # generated already exists in the database:
            while True:
                try:
                    with transaction.atomic():
                        user.save()
                        break
                except IntegrityError as exception:
                    if re.search(
                        r'Key \(username\)=\S+? already exists',
                        str(exception)
                    ) or re.search(
                        r'Duplicate entry \'\S+\' for key '
                        r'\'(users_user\.)?username\'',
                        str(exception)
                    ):
                        user.username = 'user' + random_token(7, digits)
                    else:
                        raise  # pragma: no cover
    else:
        user = request.user

    if not user.oauth:
        user.oauth = {}

    if provider not in user.oauth:
        user.oauth[provider] = {}

    user.oauth[provider][user_id] = {
        'access_info': access_info,
        'user_info': user_info,
    }
    user.save()

    login(request, user)

    if state['next']:
        return redirect(state['next'])

    return Response(user_id)


@receiver(user_registered, sender=None)
def auto_login_on_registration(user, request, **kwargs):
    login(request, user)


@receiver(user_activated, sender=None)
def grant_admin_based_on_email(user, request, **kwargs):
    if not settings.ADMINS:
        return

    admin_emails = {address for (name, address) in settings.ADMINS}
    if user.email in admin_emails:
        user.is_staff = True
        user.is_superuser = True
        user.save()
