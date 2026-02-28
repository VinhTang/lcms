from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailDomainBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        login_input = username or kwargs.get('domain') or kwargs.get('email')
        if not login_input:
            return None
            
        try:
            # Check by email OR domain OR fallback username natively
            user = User.objects.get(
                Q(email=login_input) | Q(domain=login_input) | Q(username=login_input)
            )
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
