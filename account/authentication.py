from django.contrib.auth.models import User
from account.models import Profile

class EmailAuthBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None
        
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except User.DoesNotExist:
            return None
        

def create_profile(blackend, user, *args, **kwargs):
    """
    Create user profile for social suthentication
    """
    Profile.objects.get_or_create(user=user)
    