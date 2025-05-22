

class HookManager(object):
    """
    The hook manager is a class that allows to register some hooks, and to apply them at some points
    """

    # functions : (user, main_profile) -> None
    ON_NEW_USER = []

    @classmethod
    def register_on_new_user(cls, fcn):
        """
        Do something when a new user is coming (just subscribed to the service)
        """
        cls.ON_NEW_USER.append(fcn)

    @classmethod
    def on_new_user(cls, user, main_profile):
        """
        A user has just subscribed to the service
        """
        for fcn in cls.ON_NEW_USER:
            fcn(user, main_profile)

