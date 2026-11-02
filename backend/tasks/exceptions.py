from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class DomainError(Exception):
    """Vi phạm quy tắc nghiệp vụ. Gắn `field` nếu lỗi thuộc về một trường cụ thể."""

    def __init__(self, message, field=None, code='invalid'):
        super().__init__(message)
        self.message = message
        self.field = field
        self.code = code


class InvalidTransition(DomainError):
    def __init__(self, current, target):
        super().__init__(
            f'Cannot change status from "{current}" to "{target}".',
            field='status',
            code='invalid_transition',
        )


def api_exception_handler(exc, context):
    """Biến DomainError thành HTTP 400 có cấu trúc giống lỗi validation của DRF."""
    if isinstance(exc, DomainError):
        body = {exc.field: [exc.message]} if exc.field else {'detail': exc.message}
        return Response(body, status=400)
    return drf_exception_handler(exc, context)
