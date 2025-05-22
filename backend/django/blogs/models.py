from django.db              import models

from user_mgr.models        import User

class Blog(models.Model):
    title       = models.CharField(max_length=50)
    description = models.TextField(max_length=50)
    url         = models.CharField(max_length=100)
    photo       = models.ImageField(upload_to='blogs/photo', null=True)
    facebook    = models.CharField(max_length=100)  # Facebook page URL
    twitter     = models.CharField(max_length=100)  # Twitter page URL
    user        = models.OneToOneField(User, models.CASCADE)

    def __str__(self):
        return self.title
