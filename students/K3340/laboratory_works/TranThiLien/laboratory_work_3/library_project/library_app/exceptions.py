from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def library_exception_handler(exc, context):
    """
    Попытка удалить объект, на который ссылаются другие записи
    (например, зал с читателями), возвращает 409 вместо ошибки 500.
    """
    if isinstance(exc, ProtectedError):
        return Response(
            {'detail': 'Объект нельзя удалить: на него ссылаются другие записи.'},
            status=status.HTTP_409_CONFLICT,
        )
    return exception_handler(exc, context)

from rest_framework.renderers import JSONRenderer


class UTF8JSONRenderer(JSONRenderer):
    charset = 'utf-8'