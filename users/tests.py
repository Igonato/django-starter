import json
import random
from base64 import b64encode
from http import HTTPStatus

from django.core.signing import TimestampSigner

import factory
import pytest
import requests
from pytest_factoryboy import register
from rest_framework.reverse import reverse
from rest_registration.signals import user_activated

from .models import User


@register
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'user{n}')

    class Meta:
        model = User
        django_get_or_create = ('username', )


@pytest.mark.django_db
def test_user_create():
    user = User(username='foo')
    user.set_password('bar')
    user.save()
    assert user.id


def test_user_admin(admin_client):
    response = admin_client.get('/admin/users/user/')
    assert response.status_code == HTTPStatus.OK


def test_auth_root(client):
    res = client.get(reverse('auth-root'))
    assert res.status_code == HTTPStatus.OK
    assert 'login' in res.json()


def test_oauth_urls(client, settings):
    settings.OAUTH = {'myprovider': {}}
    res = client.get(reverse('oauth'))
    assert res.status_code == HTTPStatus.OK
    assert 'myprovider' in res.json()


@pytest.mark.django_db
def test_oauth_provier(client, settings):
    settings.OAUTH = {
        'myprovider': {
            'auth_uri': 'https://myprovider.com/oauth',
            'client_id': 'myclientid',
            'client_secret': 'mysecret',
            'scope': 'myscope',
        },
    }
    res = client.get(reverse('oauth-provider', ('myprovider', )))
    assert res.status_code == HTTPStatus.FOUND
    assert res.url.startswith('https://myprovider.com/oauth')
    assert 'response_type=code' in res.url
    assert 'client_id=myclientid' in res.url
    assert 'mysecret' not in res.url
    assert 'scope=myscope' in res.url

    state_validation = client.session['state_validation']
    res = client.get(reverse('oauth-provider', ('myprovider', )))
    assert state_validation == client.session['state_validation']


@pytest.mark.django_db
def test_oauth_provier_not_found(client):
    res = client.get(reverse('oauth-provider', ('surprise', )))
    assert res.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_oauth_callback_state_validation(client, settings):
    settings.OAUTH = {'myprovider': {}}
    settings.SECRET_KEY = 'not-very-secret'

    validation = 'abc'
    bad_signature = 'surprise'
    expired_signature = '1jTfpG:vdwkxopz5nKLn3WIN6lOQDtfYTQ'

    bad_state = {b64encode(json.dumps({
        'signature': bad_signature,
        'next': None,
    }).encode('utf-8'))}

    expired_state = {b64encode(json.dumps({
        'signature': expired_signature,
        'next': None,
    }).encode('utf-8'))}

    session = client.session
    session['state_validation'] = validation
    session.save()

    res = client.get(
        reverse('oauth-callback', ('myprovider', )),
        {'state': bad_state},
    )
    assert res.status_code == HTTPStatus.FORBIDDEN
    assert res.json()['detail'] == 'State is missing or invalid.'

    res = client.get(
        reverse('oauth-callback', ('myprovider', )),
        {'state': expired_state},
    )
    assert res.status_code == HTTPStatus.FORBIDDEN
    assert res.json()['detail'] == 'State expired.'


@pytest.mark.django_db
def test_oauth_bad_token_endpoint(client, settings, monkeypatch):
    settings.OAUTH = {
        'myprovider': {
            'auth_uri': 'https://spam.eggs',
            'client_id': 'myclientid',
            'client_secret': 'mysecret',
            'scope': 'myscope',
            'token_uri': 'https://foo.bar',
        }
    }

    signer = TimestampSigner()
    state = {b64encode(json.dumps({
        'signature': signer.sign('abc').split(':', 1)[1],
        'next': None,
    }).encode('utf-8'))}
    session = client.session
    session['state_validation'] = 'abc'
    session.save()

    def fake_token_endpoint_error(url, data, headers):
        res = lambda: None
        res.status_code = HTTPStatus.BAD_REQUEST
        return res

    monkeypatch.setattr(requests, 'post', fake_token_endpoint_error)
    res = client.get(
        reverse('oauth-callback', ('myprovider', )),
        {'state': state},
    )
    assert res.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_oauth_callback_google(client, settings, monkeypatch):
    settings.OAUTH = {
        'google': {
            'auth_uri': 'https://google.com/oauth',
            'client_id': 'myclientid',
            'client_secret': 'mysecret',
            'scope': 'myscope',
            'token_uri': 'https://google.com/token',
        }
    }

    def fake_google_success(url, data, headers):
        res = lambda: None
        res.status_code = HTTPStatus.OK
        response_json = {
            'expires_in': 42,
            'token_type': 'bearer',
            'access_token': 'abc',
            'id_token': 'foo.%s.bar' % (b64encode(json.dumps({
                'sub': '123',
                'given_name': 'John',
                'family_name': 'Doe',
                'email': 'jd@example.com',
            }).encode())).decode()
        }
        res.json = lambda: response_json
        return res

    monkeypatch.setattr(requests, 'post', fake_google_success)

    signer = TimestampSigner()
    state = {b64encode(json.dumps({
        'signature': signer.sign('abc').split(':', 1)[1],
        'next': None,
    }).encode('utf-8'))}
    session = client.session
    session['state_validation'] = 'abc'
    session.save()

    res = client.get(
        reverse('oauth-callback', ('google', )),
        {'state': state},
    )
    assert res.status_code == HTTPStatus.OK
    assert res.json() == '123'


@pytest.mark.django_db
def test_oauth_callback_facebook(client, settings, monkeypatch):
    settings.OAUTH = {
        'facebook': {
            'auth_uri': 'https://facebook.com/oauth',
            'client_id': 'myclientid',
            'client_secret': 'mysecret',
            'scope': 'myscope',
            'token_uri': 'https://facebook.com/token',
        }
    }

    def fake_facebook_success(url, data, headers):
        res = lambda: None
        res.status_code = HTTPStatus.OK
        response_json = {
            'expires_in': 42,
            'token_type': 'bearer',
            'access_token': 'abc',
        }

        if url == 'https://graph.facebook.com/me':
            response_json = {
                'id': '456',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'jd@example.com'
            }

        res.json = lambda: response_json
        return res

    monkeypatch.setattr(requests, 'post', fake_facebook_success)

    signer = TimestampSigner()
    state = {b64encode(json.dumps({
        'signature': signer.sign('abc').split(':', 1)[1],
        'next': None,
    }).encode('utf-8'))}
    session = client.session
    session['state_validation'] = 'abc'
    session.save()

    res = client.get(
        reverse('oauth-callback', ('facebook', )),
        {'state': state},
    )
    assert res.status_code == HTTPStatus.OK
    assert res.json() == '456'

    def fake_facebook_me_error(url, data, headers):
        res = lambda: None
        res.status_code = HTTPStatus.OK
        response_json = {
            'expires_in': 42,
            'token_type': 'bearer',
            'access_token': 'abc',
        }

        if url == 'https://graph.facebook.com/me':
            res.status_code = HTTPStatus.BAD_REQUEST

        res.json = lambda: response_json
        return res

    monkeypatch.setattr(requests, 'post', fake_facebook_me_error)

    session = client.session
    session['state_validation'] = 'abc'
    session.save()

    res = client.get(
        reverse('oauth-callback', ('facebook', )),
        {'state': state},
    )
    assert res.status_code == HTTPStatus.FORBIDDEN
    assert 'Unable to get user info' in res.json()['detail']


@pytest.mark.django_db
def test_oauth_callback_unsupported_provider(client, settings, monkeypatch):
    settings.OAUTH = {
        'surprise': {
            'auth_uri': 'https://surprise.com/oauth',
            'client_id': 'myclientid',
            'client_secret': 'mysecret',
            'scope': 'myscope',
            'token_uri': 'https://surprise.com/token',
        }
    }

    def fake_token_success(url, data, headers):
        res = lambda: None
        res.status_code = HTTPStatus.OK
        response_json = {
            'expires_in': 42,
            'token_type': 'bearer',
            'access_token': 'abc',
        }
        res.json = lambda: response_json
        return res

    monkeypatch.setattr(requests, 'post', fake_token_success)

    signer = TimestampSigner()
    state = {b64encode(json.dumps({
        'signature': signer.sign('abc').split(':', 1)[1],
        'next': None,
    }).encode('utf-8'))}
    session = client.session
    session['state_validation'] = 'abc'
    session.save()

    res = client.get(
        reverse('oauth-callback', ('surprise', )),
        {'state': state},
    )
    assert res.status_code == HTTPStatus.FORBIDDEN
    assert 'Unable to get user info' in res.json()['detail']


@pytest.mark.django_db
def test_oauth_username_collision(client, settings, monkeypatch):
    settings.OAUTH = {
        'facebook': {
            'auth_uri': 'https://facebook.com/oauth',
            'client_id': 'myclientid',
            'client_secret': 'mysecret',
            'scope': 'myscope',
            'token_uri': 'https://facebook.com/token',
        }
    }

    def fake_facebook_success(url, data, headers):
        res = lambda: None
        res.status_code = HTTPStatus.OK
        response_json = {
            'expires_in': 42,
            'token_type': 'bearer',
            'access_token': 'abc',
        }

        if url == 'https://graph.facebook.com/me':
            response_json = {
                'id': '456',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'jd@example.com'
            }

        res.json = lambda: response_json
        return res

    def fake_random_choice(alphabet, invoked=[0]):
        invoked[0] += 1
        if invoked[0] > 50:
            return 'y'
        return 'x'

    monkeypatch.setattr(random, 'choice', fake_random_choice)
    monkeypatch.setattr(requests, 'post', fake_facebook_success)

    User(username='userxxxxxxx', email='asdf@asdf').save()

    signer = TimestampSigner()
    state = {b64encode(json.dumps({
        'signature': signer.sign('abc').split(':', 1)[1],
        'next': None,
    }).encode('utf-8'))}
    session = client.session
    session['state_validation'] = 'abc'
    session.save()

    res = client.get(
        reverse('oauth-callback', ('facebook', )),
        {'state': state},
    )
    assert res.status_code == HTTPStatus.OK

    client.logout()
    session = client.session
    session['state_validation'] = 'abc'
    session.save()

    res = client.get(
        reverse('oauth-callback', ('facebook', )),
        {'state': state},
    )
    assert res.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_oauth_existing_user(client, settings, monkeypatch, user):
    settings.OAUTH = {
        'facebook': {
            'auth_uri': 'https://facebook.com/oauth',
            'client_id': 'myclientid',
            'client_secret': 'mysecret',
            'scope': 'myscope',
            'token_uri': 'https://facebook.com/token',
        }
    }

    def fake_facebook_success(url, data, headers):
        res = lambda: None
        res.status_code = HTTPStatus.OK
        response_json = {
            'expires_in': 42,
            'token_type': 'bearer',
            'access_token': 'abc',
        }

        if url == 'https://graph.facebook.com/me':
            response_json = {
                'id': '456',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'jd@example.com'
            }

        res.json = lambda: response_json
        return res

    monkeypatch.setattr(requests, 'post', fake_facebook_success)

    signer = TimestampSigner()
    state = {b64encode(json.dumps({
        'signature': signer.sign('abc').split(':', 1)[1],
        'next': None,
    }).encode('utf-8'))}
    session = client.session
    session['state_validation'] = 'abc'
    session.save()

    client.force_login(user)

    res = client.get(
        reverse('oauth-callback', ('facebook', )),
        {'state': state},
    )
    assert res.status_code == HTTPStatus.OK

    user.refresh_from_db()
    assert user.oauth['facebook']['456']


@pytest.mark.django_db
def test_oauth_next_redirect(client, settings, monkeypatch):
    settings.OAUTH = {
        'facebook': {
            'auth_uri': 'https://facebook.com/oauth',
            'client_id': 'myclientid',
            'client_secret': 'mysecret',
            'scope': 'myscope',
            'token_uri': 'https://facebook.com/token',
        }
    }

    def fake_facebook_success(url, data, headers):
        res = lambda: None
        res.status_code = HTTPStatus.OK
        response_json = {
            'expires_in': 42,
            'token_type': 'bearer',
            'access_token': 'abc',
        }

        if url == 'https://graph.facebook.com/me':
            response_json = {
                'id': '456',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'jd@example.com'
            }

        res.json = lambda: response_json
        return res

    monkeypatch.setattr(requests, 'post', fake_facebook_success)

    signer = TimestampSigner()
    state = {b64encode(json.dumps({
        'signature': signer.sign('abc').split(':', 1)[1],
        'next': '/welcome',
    }).encode('utf-8'))}
    session = client.session
    session['state_validation'] = 'abc'
    session.save()

    res = client.get(
        reverse('oauth-callback', ('facebook', )),
        {'state': state},
    )
    assert res.status_code == HTTPStatus.FOUND
    assert 'welcome' in res.url


@pytest.mark.django_db
def test_oauth_callback_provider_not_found(client):
    res = client.get(reverse('oauth-callback', ('surprise', )))
    assert res.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_register_signal_login(client):
    res = client.post(
        reverse('rest_registration:register'),
        data={
            'username': 'foo',
            'email': 'bar@baz.spam',
            'password': 'x@j(w2wxu^038614b',
            'password_confirm': 'x@j(w2wxu^038614b',
        }
    )
    assert res.status_code == HTTPStatus.CREATED


@pytest.mark.django_db
def test_activated_signal_admin(client, user, settings):
    user_activated.send(sender=None, user=user, request=None)
    user.refresh_from_db()
    assert not user.is_superuser

    settings.ADMINS = [('John', 'admin@example.com')]
    user.email = 'surprise@example.com'
    user.save()
    user_activated.send(sender=None, user=user, request=None)
    user.refresh_from_db()
    assert not user.is_superuser

    user.email = 'admin@example.com'
    user.save()
    user_activated.send(sender=None, user=user, request=None)
    user.refresh_from_db()
    assert user.is_superuser
