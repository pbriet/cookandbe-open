
from django.contrib.auth            import login as django_login
from django.contrib.auth.backends   import ModelBackend
from django.core.exceptions         import PermissionDenied

from common.date                    import today

from optalim.settings               import OP_ENABLE_PUBLIC_PAYMENT

from user_mgr.models                import User, ProUser

def authenticate(app, **credentials):
    """
    Returns a user if authentication succeeds.
    None otherwise
    """
    backend = APP_TO_LOGIN_BACKEND[app]()
    try:
        user = backend.authenticate(**credentials)
    except TypeError:
        # This backend doesn't accept these credentials as arguments. Try the next one.
        return None
    except PermissionDenied:
        # This backend says to stop in our tracks - this user should not be allowed in at all.
        return None
    return user

def login(request, user, app):
    """
    Login the user, checks and updates the subscription validity

    Returns {"expired": has the subscription just expired ?}
    And updates - if required - user.subscription_level
    """
    # Backend used for login
    user.backend = APP_TO_LOGIN_BACKEND_IMPORT[app]
    django_login(request, user)

def update_user_subscription_level(user):
    """
    Returns True if the subscription has just expired.
    Updates the user to reflects this.
    """
    if not isinstance(user, User):
        return False
    if not OP_ENABLE_PUBLIC_PAYMENT:
        return False

    expired = False
    # Checking the subscription validity
    level = 0 # Default = no active subscription : "free" level
    subscription = user.current_subscription
    if subscription is not None:
        level = subscription.level
    elif user.has_promo_code_benefit("PREMIUM"):
        level = 2
    elif user.subscription_level > level:
        expired = True

    if user.subscription_level != level:
        user.subscription_level = level
        user.save()

    return expired



class OpAuthBackend(ModelBackend):
    """
    Backend to authenticate and retrieve users  (assigned to the Request objects)
    """
    USER_MODEL = None

    def authenticate(self, request=None, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(self.USER_MODEL.USERNAME_FIELD)
        try:
            user = self.USER_MODEL._default_manager.get_by_natural_key(username)
            if user.check_password(password):
                return user
        except self.USER_MODEL.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            self.USER_MODEL().set_password(password)

    def get_user(self, user_id):
        try:
            return self.USER_MODEL._default_manager.get(pk=user_id)
        except self.USER_MODEL.DoesNotExist:
            return None



class PublicAuthBackend(OpAuthBackend):
    USER_MODEL = User

class ProAuthBackend(OpAuthBackend):
    USER_MODEL = ProUser


APP_TO_LOGIN_BACKEND = {
    'public': PublicAuthBackend,
    'pro':    ProAuthBackend
}

APP_TO_USER_MODEL = {
    'public': User,
    'pro':    ProUser
}

APP_TO_LOGIN_BACKEND_IMPORT = {}
for key, cls in APP_TO_LOGIN_BACKEND.items():
    APP_TO_LOGIN_BACKEND_IMPORT[key] = 'user_mgr.auth.%s' % cls.__name__
