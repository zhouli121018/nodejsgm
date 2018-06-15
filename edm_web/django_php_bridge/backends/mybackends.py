from django.contrib.auth.backends import ModelBackend
from app.core.models import Customer

class CustomerUserBackend(ModelBackend):

    def authenticate(self, username=None, password=None, t_password=None, **kwargs):
        UserModel = Customer
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
            if user.check_password(password, t_password):
                return user
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)


    def get_user(self, user_id):
        UserModel = Customer
        try:
            return UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


