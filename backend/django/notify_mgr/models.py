from django.db              import models
from user_mgr.models        import User

class Information(models.Model):
    """
    Something to add in the news feed
    """
    title           = models.CharField(max_length=200)
    content         = models.TextField()
    action          = models.CharField(max_length=40) # Action to do to "solve" the issue / link to page
    priority        = models.IntegerField(default=1)
    readers         = models.ManyToManyField(User) # Who has read the message ?
    valid_until     = models.DateTimeField() # Until when this message should be displayed
    creation_date   = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kargs):
        self.can_be_read = True
        self.label = "info"
        if 'can_be_read' in kargs:
            # If can_be_read is False, the user is unable to set it as read
            self.can_be_read = kargs.pop('can_be_read')
        if 'label' in kargs:
            self.label = kargs.pop('label')
        models.Model.__init__(self, *args, **kargs)
