
from django.db                  import models
from django.dispatch            import receiver

from common.model               import AutoUrlKeyModel, enable_auto_url_key

from user_mgr.models            import User

@enable_auto_url_key
class Publication(AutoUrlKeyModel, models.Model):
    # Function that returns the string from which the url_key will be built
    URL_KEY_FROM_FCN = lambda x: x.question.strip()

    author          = models.ForeignKey(User, models.CASCADE, null = True, default = None)
    question        = models.TextField(null = True, default = None)
    response        = models.TextField(null = True, default = None)
    creation_date   = models.DateTimeField(auto_now_add = True)
    public          = models.BooleanField(default = False)
    user_sex        = models.BooleanField(default = True) # { False: male, True: female }
    user_date       = models.DateField()

    PUBLIC_FIELDS   = "author", "question", "creation_date", "user_sex", "user_date", "url_key"

class Discussion(models.Model):
    owner           = models.ForeignKey(User, models.CASCADE, related_name = "discussions")
    dietician       = models.ForeignKey(User, models.SET_NULL, null = True, default = None, related_name = "patient_discussions")
    title           = models.CharField(max_length = 150)
    close_date      = models.DateTimeField(null = True, default = None)
    creation_date   = models.DateTimeField(auto_now_add = True)
    publication     = models.OneToOneField(Publication, models.CASCADE, null = True, default = None, related_name = "discussion")

    # Database duplication to faster queries
    last_date       = models.DateTimeField(null = True, default = None)

    # Should be in a dedicated table (Reading) but increase performances for now
    owner_read_date     = models.DateTimeField(null = True, default = None)
    dietician_read_date = models.DateTimeField(null = True, default = None)

    @property
    def last_update(self):
        if self.messages.count() == 0:
            return None
        return self.messages.all().order_by("-date")[0].date

    def nb_unread_messages(self, reader_id = None):
        if reader_id is not None and reader_id == self.owner_id:
            date = self.owner_read_date
        elif reader_id is not None and reader_id == self.dietician_id:
            date = self.dietician_read_date
        else:
            # En l'abscence de reader on considère tout message non lu par au moins 1 des 2 personnes
            if None in (self.owner_read_date, self.dietician_read_date):
                date = None
            else:
                date = min(self.owner_read_date, self.dietician_read_date)
        if date is None:
            return self.messages.count()
        return self.messages.filter(date__gt = date).count()

# class Reading(models.Model):
    # reader          = models.ForeignKey(User, related_name = "readings")
    # discussion      = models.ForeignKey(Discussion, related_name = "readers")
    # date            = models.DateTimeField(auto_now_add = True)

class Message(models.Model):
    discussion      = models.ForeignKey(Discussion, models.CASCADE, related_name = "messages")
    author          = models.ForeignKey(User, models.CASCADE, related_name = "messages")
    content         = models.TextField()
    date            = models.DateTimeField(auto_now_add = True)

@receiver(models.signals.post_save, sender = Message)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if not created:
        return
    discussion = instance.discussion
    if discussion.dietician is None and instance.author.is_dietician:
        discussion.dietician = instance.author
    if instance.author.id == discussion.owner_id:
        discussion.owner_read_date = instance.date
    if instance.author.id == discussion.dietician_id:
        discussion.dietician_read_date = instance.date
    discussion.last_date = instance.date
    discussion.save()

