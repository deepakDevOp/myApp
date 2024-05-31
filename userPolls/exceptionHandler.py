from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from rest_framework import serializers


def custom_exception_handler(exc, context):
    # Call the default exception handler first
    response = exception_handler(exc, context)

    # If the exception is AuthenticationFailed, return custom error response
    if isinstance(exc, AuthenticationFailed):
        return Response({'error': exc.detail}, status=exc.status_code)
    return response
