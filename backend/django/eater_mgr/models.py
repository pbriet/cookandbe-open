from django.db                  import models
from user_mgr.models            import User

from profile_mgr.models         import Profile

class Eater(models.Model):
    """
    People known by user (can be friends or family).
    Frequent eaters are tagged regular.
    """
    user                = models.ForeignKey(User, models.CASCADE, related_name="eaters")
    profile             = models.ForeignKey(Profile, models.CASCADE)
    regular             = models.BooleanField(default=True)
