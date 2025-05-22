from django.db              import models
from user_mgr.models        import User

class Newsletter(models.Model):
    """
    A newsletter
    """
    created_at    = models.DateTimeField(auto_now_add=True)
    sent_at       = models.DateTimeField(null=True, blank=True)
    sent_by       = models.ForeignKey(User, models.SET_NULL, null=True, blank=True)
    subject       = models.CharField(max_length = 200)
    content       = models.TextField()
    template_name = models.CharField(max_length = 100, null=True) # If imported from Mandrill, what is the template name