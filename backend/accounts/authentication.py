from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

TOKEN_TTL = timedelta(days=getattr(settings, 'AUTH_TOKEN_TTL_DAYS', 14))


class ExpiringTokenAuthentication(TokenAuthentication):
    """Token hết hạn sau TOKEN_TTL kể từ lúc cấp (đăng nhập lại để lấy token mới)."""

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if token.created + TOKEN_TTL < timezone.now():
            token.delete()
            raise AuthenticationFailed('Token has expired.')
        return user, token
