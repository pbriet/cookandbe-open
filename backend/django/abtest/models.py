from django.db                  import models
from user_mgr.models            import User



class AbCampaign(models.Model):
    """
    A/B testing campaign
    """
    key                 = models.CharField(max_length=30, unique=True, db_index=True)
    description         = models.TextField()
    created_at          = models.DateTimeField(auto_now_add=True)
    # JIM:
    #suspended: possibilité de suspendre une campagne
    #user_limit: possibilité de limiter le nombre de testeurs
    #time_limit: possibilité de limiter dans le temps
    #default_option: option utilisée par les users n'ayant pas participé à la campagne lorsque celle-ci est suspendue ou terminée (limite atteinte)

    def __str__(self):
        return self.key


class AbOption(models.Model):
    """
    Options available for this campaign
    """
    campaign            = models.ForeignKey(AbCampaign, models.CASCADE, related_name='options')
    key                 = models.CharField(max_length=30)

    def __str__(self):
        return self.campaign.key + " | " + self.key


class AbChoice(models.Model):
    """
    Option activated for one user
    """
    campaign            = models.ForeignKey(AbCampaign, models.CASCADE, related_name="choices")
    unique_id           = models.CharField(max_length=80)  # Retrieved from Ganalytics
    user                = models.ForeignKey(User, models.CASCADE, null=True)
    option              = models.ForeignKey(AbOption, models.CASCADE)

class AbRecord(models.Model):
    """
    User actions related to A/B testing
    """
    choice              = models.ForeignKey(AbChoice, models.CASCADE, related_name="records")
    objective           = models.CharField(max_length=30)  # Objective reached  (e.g. "clicked_buy")
