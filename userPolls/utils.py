from django.utils import timezone
from oauthlib.common import generate_token
from datetime import timedelta
from oauth2_provider.models import AccessToken
import secrets
import string
from django.core.mail import send_mail


def update_access_token(user=None):
    token_obj = AccessToken.objects.get(user_id=user.id)
    expires = timezone.now() + timedelta(days=30)
    token = generate_token()
    token_obj.token = token
    token_obj.expires = expires
    token_obj.save()
    return token_obj


def generate_oauth_token_save_in_db(user):
    # function to generate oauth token for the user on first time signup
    # Create an OAuth2 application (if not already created)
    expires = timezone.now() + timedelta(days=30)
    token = generate_token()
    access_token = AccessToken.objects.create(
        user=user,
        token=token,
        expires=expires,
        scope='read write',  # Customize scopes as needed
        application=None
    )
    access_token.user_id = user.pk
    access_token.save()
    return access_token


def generate_alphanumeric_otp(length=6):
    alphanumeric_chars = string.ascii_letters + string.digits
    otp = ''.join(secrets.choice(alphanumeric_chars) for _ in range(length))
    return otp


def create_save_username(user):
    username = str(user.id) + '_' + user.phone_number
    user.username = username
    user.save()
    return user


def send_otp(otp=None, email=None):
    subject = 'Password Reset OTP'
    message = f'Hello,\n You have requested to reset your password. ' \
              f'Please use the following OTP (One-Time Password) to reset your password.\nOTP: {otp}\n' \
              f'If you did not request this password reset, please ignore this email. ' \
              f'Your password will remain unchanged.\n' \
              f'Thank you,\n' \
              f'WHM team'
    send_mail(subject, message, None, [email])


def extract_error_message(error):
    updated_errors = {}
    if isinstance(error, dict):
        for key, value in error.items():
            if key == "non_field_errors":
                return value[0]
            updated_errors[key] = value[0]
        return updated_errors
    return error
