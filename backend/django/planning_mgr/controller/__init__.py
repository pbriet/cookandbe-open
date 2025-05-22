
MEAL_FULL_PREFETCH = ('dishes__dish_type',
                      #'dishes__dish_recipe_filters',
                      #'dishes__dish_food_filters',
                      'meal_type',
                      'meal_place',
                      'eaters__profile',
                      'dishes__dishrecipe_set__recipe')

DAY_FULL_PREFETCH = tuple('meal_slots__%s' % p for p in MEAL_FULL_PREFETCH)
