from django.db                  import models
from user_mgr.models            import User

class Question(models.Model):
    author          = models.ForeignKey(User, models.CASCADE)
    title           = models.CharField(max_length=200)
    description     = models.TextField()
    created_at      = models.DateTimeField(auto_now_add=True)
    closed_at       = models.DateTimeField(null=True, default=None, blank=True)

class Choice(models.Model):
    question        = models.ForeignKey(Question, models.CASCADE, related_name="choices")
    text            = models.CharField(max_length=200)

class Answer(models.Model):
    question        = models.ForeignKey(Question, models.CASCADE, related_name="answers")
    user            = models.ForeignKey(User, models.CASCADE)
    choice          = models.ForeignKey(Choice, models.CASCADE)
    comment         = models.TextField(null=True, blank=True, default=None)

    class Meta:
        unique_together = ("question", "user", "choice")
