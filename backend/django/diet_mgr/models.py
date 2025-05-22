from django.db                  import models
from django.core.cache          import cache
from common.model               import NamedModel
from optalim.settings           import OP_ENABLE_PUBLIC_PAYMENT

class Diet(models.Model):
    """
    Describe a diet. The resulting constraints are then defined by Hippocrate.
    """
    # Each diet is managed by a handler. Its role is to create
    # the constraints given a profile. They are auto-registered in this class
    _handlers = {}

    key                     = models.CharField(max_length = 32)
    title                   = models.CharField(max_length = 64)
    email_title             = models.CharField(max_length = 64)
    description             = models.CharField(max_length = 512)
    excluded_food_tags      = models.ManyToManyField('recipe_mgr.FoodTag', related_name="diets_with_exclusion")  # Recipes with this food tag will be excluded
    forewarned_food_tags    = models.ManyToManyField('recipe_mgr.FoodTag', related_name="diets_with_warning")    # Recipes with this food tag will be signaled
    included_food_tags      = models.ManyToManyField('recipe_mgr.FoodTag', related_name="diets_with_inclusion")  # Recipes with this food tag will be encouraged
    default_display         = models.BooleanField(default=True)  # Is this diet displayed by default on premium selection page
    enabled                 = models.BooleanField(default=False) # Is this diet available to public
    min_subscription_level  = models.IntegerField(default=0)     # 0: free, 1: freedom, 2: premium
    has_diagnostic          = models.BooleanField(default=False) # Are there any question the user should answer ?

    free_trial_days         = models.IntegerField(default=7)     # Number of days with free trial

    # Key displayed in urls of diet-dedicated pages
    url_key                 = models.CharField(max_length=500, db_index=True)
    rank                    = models.IntegerField(default=1)

    @classmethod
    def register_diet_handler(cls, key, diet_handler):
        cls._handlers[key] = diet_handler

    def __str__(self):
        return self.key

    def get_min_subscription_level(self):
        if not OP_ENABLE_PUBLIC_PAYMENT:
            return 0
        return self.min_subscription_level

    @classmethod
    def get_cached(cls, diet_id):
        cache_key = 'diet:%i' % diet_id
        cached = cache.get(cache_key)
        if cached:
            return cached
        value = cls.objects.prefetch_related('excluded_food_tags', 'included_food_tags').get(pk=diet_id)
        cache.set(cache_key, value)
        return value

    def handler_cls(self):
        if self.key is None:
            return self._handlers["balanced"]
        return self._handlers[self.key]

    def handler(self, profile, **kargs):
        """
        Returns the handler for this diet
        """
        return self.handler_cls()(self, profile, **kargs)

class UserDietParameter(models.Model):
    """
    Parameters to configure the use of a diet for a given user
    """
    class Meta:
        unique_together = ("user", "name")

    user            = models.ForeignKey("user_mgr.User", models.CASCADE, related_name = "diet_parameters")
    name            = models.CharField(max_length = 16)
    float_value     = models.FloatField(null = True)
    string_value    = models.CharField(max_length = 64, null = True)