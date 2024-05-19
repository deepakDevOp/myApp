from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser


class CustomIsAuthenticated(IsAuthenticated):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            raise AuthenticationFailed('Token does not exist.')
        is_authenticated = super().has_permission(request, view)
        if not is_authenticated:
            raise AuthenticationFailed('Either token is not provided or has expired.')
        return is_authenticated