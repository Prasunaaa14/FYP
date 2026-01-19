from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Use username field instead of email to avoid MultipleObjectsReturned
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # If multiple users exist, return None for security
            return None

        if user.check_password(password):
            return user
        return None
