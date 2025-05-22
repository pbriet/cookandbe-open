from django.contrib     import admin
from recipe_mgr.models  import Food, Recipe, DishType, FoodType, FoodTag,\
                               FoodSource, CookingMethod, RawState,\
                               DishTypeAggregation, RecipeTag,\
                               FoodSeasonality, Ustensil, DishTypeUnion

admin.site.register(Food)
admin.site.register(Recipe)
admin.site.register(DishType)
admin.site.register(DishTypeAggregation)
admin.site.register(DishTypeUnion)
admin.site.register(FoodType)
admin.site.register(FoodTag)
admin.site.register(FoodSource)
admin.site.register(CookingMethod)
admin.site.register(RawState)
admin.site.register(RecipeTag)
admin.site.register(FoodSeasonality)
admin.site.register(Ustensil)

