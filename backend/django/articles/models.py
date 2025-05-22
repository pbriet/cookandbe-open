from common.model           import AutoUrlKeyModel, enable_auto_url_key, auto_delete_file
from django.db              import models
from user_mgr.models        import User

@enable_auto_url_key
@auto_delete_file('photo')
class Article(AutoUrlKeyModel, models.Model):
    """
    An article
    """
    # Function that returns the string from which the url_key will be built
    URL_KEY_FROM_FCN = lambda x: x.title.strip()

    created_at    = models.DateTimeField(auto_now_add=True)
    created_by    = models.ForeignKey(User, models.SET_NULL, null=True)
    title         = models.CharField(max_length = 200)
    summary       = models.TextField()  # Short version of the article (max. 5 lines, pure text)
    content       = models.TextField()  # Full version of the article (HTML)
    meta_desc     = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    photo         = models.ImageField(upload_to='articles', null=True)
    published     = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class ArticleImage(models.Model):
    """
    An image to include in an article
    """
    article       = models.ForeignKey(Article, models.CASCADE, related_name="images")
    photo         = models.ImageField(upload_to='articles', null=True)
