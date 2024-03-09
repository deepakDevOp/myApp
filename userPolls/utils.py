from django.utils import timezone
from oauthlib.common import generate_token
from datetime import timedelta
from oauth2_provider.models import AccessToken
import secrets
import string


def generate_oauth_token_save_in_db(user):
    # function to generate oauth token for the user on first time signup
    expires = timezone.now() + timedelta(hours=48)
    token = generate_token()
    access_token = AccessToken.objects.create(
        user=user,
        token=token,
        expires=expires,
        scope='read write',  # Customize scopes as needed
        application=None  # Assuming this is a confidential client
    )
    return access_token


def generate_alphanumeric_otp(length=6):
    alphanumeric_chars = string.ascii_letters + string.digits
    otp = ''.join(secrets.choice(alphanumeric_chars) for _ in range(length))
    return otp
