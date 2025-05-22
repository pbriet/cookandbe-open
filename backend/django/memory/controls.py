
from django.db.models                   import Prefetch

from hippocrate_cpp.core                import FoodIndex, FoodTagList
from recipe_mgr.models                  import Food, FoodConversion
from shopping_mgr.models                import ShoppingCategory

def initFoodIndex():
    food_index = FoodIndex()
    shopping_conversions = FoodConversion.objects.filter(shopping_compatible=True)
    food_prefetch = ('type', 'default_conversion', 'tags', Prefetch('conversions', queryset=shopping_conversions, to_attr="shopping_conversions"))
    for food in Food.objects.prefetch_related(*food_prefetch).all():
        if food.type.usually_stored or (food.fresh_expiry is None and food.type.fresh_expiry is None):
            food_minimum = 0
        elif food.default_conversion is not None and food.default_conversion.shopping_compatible is True:
            food_minimum = food.default_conversion.value
        else:
            food_conversions = list(cnv.value for cnv in food.shopping_conversions if cnv.value > 1.0)
            if len(food_conversions) > 0:
                food_minimum = min(food_conversions)
            else:
                food_minimum = 0
        food_tags_set = set()
        for tag in food.tags.all():
            food_tags_set.add(tag.id)
            food_tags_set = food_tags_set.union(tag.cached_parents_ids())
        food_tags = FoodTagList()
        for tag in food_tags_set:
            food_tags.append(tag)
        # print("adding food index", food.id, food_minimum, len(food_tags))
        food_index.add_food(food.id, float(food_minimum), food_tags)
    return food_index

def initShoppingCategoriesOrder():
    return dict((category.name, category.list_order) for category in ShoppingCategory.objects.all())

class MemoryManager:

    @classmethod
    def initialize(cls):
        cls.food_index = initFoodIndex()
        cls.shopping_categories_order = initShoppingCategoriesOrder()


