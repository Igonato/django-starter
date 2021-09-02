from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse


def format_doc(*args, **kwargs):
    def wrap(func):
        func.__doc__ = func.__doc__.format(*args, **kwargs)
        return func
    return wrap


@api_view(['GET'])
@permission_classes([AllowAny])
@format_doc(**settings.META)
def home(request, format=None):
    """
    # Hello, World!

    This is the REST API root for {NAME} project.

    You `can` _use_ **Markdown** to document your API.

    {DESCRIPTION}

    Explore available endpoint using the links below:
    """
    return Response({
        'auth': reverse('auth-root', request=request),
    })
