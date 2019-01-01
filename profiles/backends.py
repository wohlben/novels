from django.contrib.auth import get_user_model as _get_user_model
from django.contrib.auth.backends import ModelBackend as _ModelBackend
import logging
from uuid import UUID

_UserModel = _get_user_model()
_logger = logging.getLogger("profiles.token_auth")


class TokenAuthBackend(_ModelBackend):
    def get_user(self, user_id):
        try:  # pragma: no cover
            return _UserModel.objects.get(pk=user_id)
        except _UserModel.DoesNotExist:
            return None

    def authenticate(self, login_token=None):
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
