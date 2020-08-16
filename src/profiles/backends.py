from django.contrib.auth import get_user_model as _get_user_model
from django.contrib.auth.backends import ModelBackend as _ModelBackend, RemoteUserBackend
from rest_framework.authentication import BaseAuthentication as _BaseAuthentication
from requests import get as _get
from .models import User
import jwt as _jwt
import logging
from uuid import UUID

_UserModel = _get_user_model()
_logger = logging.getLogger("profiles.token_auth")

_public_key = (
    "-----BEGIN PUBLIC KEY-----\n"
    + _get("https://auth.wohlben.de/auth/realms/wohlben").json().get("public_key")
    + "\n-----END PUBLIC KEY-----"
)


def bearer_auth(request):
    try:
        if header := request.META.get("HTTP_AUTHORIZATION"):
            if header.lower().startswith("bearer "):
                _, token_string = header.split(" ")
                token = _jwt.decode(token_string, _public_key, audience="wommels", verify=True, algorithms="RS256")
                try:
                    username = token.get("preferred_username")
                    user = User.objects.get(username=username)
                    if user.oidc_id is None:
                        user.oidc_id = token.get("uuid")
                        user.save()
                    elif user.oidc_id != token.get("uuid"):
                        user = User.objects.get(oidc_id=token.get("uuid"))
                    _logger.debug(f"authenticated {user.username}")
                    return user
                except User.DoesNotExist:
                    user = User.objects.create(oidc_id=token.get("uuid"))
                    _logger.info(f"created new user {user.username}")
                    return user
    except Exception as e:
        _logger.error(e)
    return None


class BearerAuth(RemoteUserBackend):
    def authenticate(self, request, remote_user):
        user = bearer_auth(request)
        return user, None


class APIBearerAuth(_BaseAuthentication):
    def authenticate(self, request):
        user = bearer_auth(request)
        return (user, None) if user else None


class TokenAuthBackend(_ModelBackend):
    def get_user(self, user_id):
        try:  # pragma: no cover
            return _UserModel.objects.get(pk=user_id)
        except _UserModel.DoesNotExist:
            return None

    def authenticate(self, login_token, **kwargs):
        try:
            username, token = login_token.split(":")
            user_qs = _UserModel.objects.filter(username=username)
            if user_qs.count() == 0:
                _logger.info(f"{username} is not a valid username")
                return None
            elif user_qs.count() > 1:
                _logger.exception(f"{username} has {user_qs.count()} matches.")

            login_token = UUID(token, version=4)
            user = user_qs.first()
            if user.login_token != login_token:
                _logger.warning(f"{username} provided an incorrect token")
                return None
            if not user.enable_login_token:
                return None
            _logger.info(f"authenticated {username}")
            return user
        except ValueError:
            _logger.info(f"somebody didn'nt specify a username")
            return None
        except Exception as e:
            _logger.error("failed to authenticate")
            raise
