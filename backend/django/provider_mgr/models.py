from django.db                  import models
from recipe_mgr.models          import NamedModel

class FoodProvider(NamedModel, models.Model):
    """
    Entity providing food to the users (vegetable basket, cafeteria, ...)
    """
    name = models.CharField(max_length = 64) # Will eventually move to a Company table
