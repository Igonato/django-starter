from http import HTTPStatus

import pytest

from .models import User


@pytest.mark.django_db
def test_user_create():
    user = User(username='foo')
    user.set_password('bar')
    user.save()
    assert user.id


def test_user_admin(admin_client):
    response = admin_client.get('/admin/users/user/')
    assert response.status_code == HTTPStatus.OK
