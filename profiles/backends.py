from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


UserModel = get_user_model()


class TokenAuthBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

    def authenticate(self, login_token=None):
        user = UserModel.objects.filter(login_token=login_token)
        if user.count() != 1:
            print("unexpected count " + str(user.count()))
            return None
        user = user.first()
        if not user.enable_login_token:
            print("disabled token")
            return None
        return user