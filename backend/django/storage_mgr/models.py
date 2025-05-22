from django.db                  import models
from user_mgr.models            import User

from recipe_mgr.models          import Food
from provider_mgr.models        import FoodProvider

class FoodStock(models.Model):
    """
    Contains already available food
    """
    user                = models.ForeignKey(User, models.CASCADE)
    food                = models.ForeignKey(Food, models.CASCADE)
    grams               = models.FloatField()
    expiry              = models.DateField(default = None, null = True)
    # provider            = models.ForeignKey(FoodProvider, default = None, null = True)
    # brand               = models.ForeignKey(Brand)
    # shopping_item       = models.ForeignKey(ShoppingItem)
