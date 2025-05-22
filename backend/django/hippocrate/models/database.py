from django.db                  import models
from user_mgr.models            import User

# Model classes imported from other Django applications (stored in database)
from recipe_mgr.models          import FoodType, Food, FoodTag, FoodTagSet, FoodConversion
from recipe_mgr.models          import Recipe, Ingredient, RecipeDishType, DishType, DishTypeAggregation
from recipe_mgr.models          import DishTypeUnion
from recipe_mgr.models          import CookingMethod, RawState
from nutrient.models            import Nutrient
from planning_mgr.models        import MetaPlanning, MealSlot, Dish, MealSlotEater, DishRecipe
from storage_mgr.models         import FoodStock
from profile_mgr.models         import Profile, Taste, RestrictedFood
from eater_mgr.models           import Eater
from diet_mgr.models            import Diet
