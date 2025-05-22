from django.db                  import models
from django.db.models           import Min, Max
from django.utils               import timezone

from common.model               import NamedModel

from planning_mgr.models        import Day, DishRecipe

from provider_mgr.models        import FoodProvider

from recipe_mgr.models          import Food, RawState

from user_mgr.models            import User

class ShoppingList(models.Model):
    """
    A shopping list
    """
    user                = models.ForeignKey(User, models.CASCADE, related_name="shopping_lists")
    creation_date       = models.DateTimeField(auto_now_add=True, blank=True)
    start_date          = models.DateField()
    end_date            = models.DateField()

class ShoppingItem(models.Model):
    """
    Inclusion of one food from a dish recipe, with its quantity
    """
    shopping_list       = models.ForeignKey(ShoppingList, models.CASCADE, related_name="items")
    food                = models.ForeignKey(Food, models.CASCADE, null=True)
    raw_state           = models.ForeignKey(RawState, models.CASCADE, null=True)
    grams               = models.FloatField(null=True) # Including loss
    got_it              = models.BooleanField(default=True) # got_it == True <> User already purchased it / got it in stock
    forced_quantity     = models.TextField(null=True)
    forced_name         = models.TextField(null=True)

    is_custom           = property(lambda x: x.food_id is None)
    fresh_expiry        = property(lambda x: x.is_custom is not None and (x.food.fresh_expiry or x.food.type.fresh_expiry))

class ShoppingCategory(NamedModel, models.Model):
    """
    In what department you can find this product (in a supermarket)
    """
    name                = models.CharField(max_length=100)
    list_order          = models.IntegerField(null=True, default=None) # Order of appearance in the shopping_list
