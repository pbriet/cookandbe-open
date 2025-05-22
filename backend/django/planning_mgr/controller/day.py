
from planning_mgr.controller        import DAY_FULL_PREFETCH
from planning_mgr.iterators         import iter_recipes
from planning_mgr.models            import Day

from recipe_mgr.models              import DishType

import random

def get_planned_days(date):
    """
    Return the list of Day objects planned for a given date
    Fully prefetched
    """
    return Day.objects.filter(date=date, skipped=False).select_related(
                              'user').prefetch_related(*DAY_FULL_PREFETCH)

def pick_best_recipes_from_day(day, max_nb=2, with_score=False, min_rating=5):
    """
    From a given day, returns the best recipes :
    - with photo
    - not too simple
    - with interesting dish_types
    """
    # Recipe : rating
    recipe_rating = {}

    for recipe in iter_recipes([day], ms_kargs={'suggest': True, 'is_cooked': True}):
        if not recipe.photo:
            # "recipe.photo is not None" doesn't work correctly. Photo object may exist without a file.
            continue
        rating = 0

        nb_ingredients = recipe.ingredients.count()
        if nb_ingredients <= 3:
            rating -= 10 # Product/recipe
        else:
            # Real recipe
            # +1 point per ingredient over 3
            rating += min(nb_ingredients - 3, 5)

        if not recipe.auto_photo:
            rating += 5 # With a photo, oh yeah !

        dish_types = [dt.name for dt in recipe.dish_types.all()]
        if DishType.DT_MAIN_COURSE in dish_types or DishType.DT_FULL_COURSE in dish_types:
            rating += 3 # Better if it is a main course

        if min_rating is None or rating >= min_rating:
            recipe_rating[recipe] = rating

    res = sorted(recipe_rating.items(), key=lambda x: x[1], reverse=True)
    if not with_score:
        res = [r[0] for r in res]
    return res[:max_nb]


def pick_recipe_to_evaluate(day):
    """
    From a past day, retrieves one recipe that the user may rate/comment
    """
    # User ratings
    user_ratings = day.user.recipe_ratings.all()
    rated_recipe_ids = set(rating.recipe_id for rating in user_ratings)

    potential_recipes = {}

    for recipe in iter_recipes([day], ms_kargs={'suggest': True, 'is_cooked': True}, dish_kargs={'activated': True}):
        if not recipe.photo:
            # "recipe.photo is not None" doesn't work correctly. Photo object may exist without a file.
            continue
        if recipe.id in rated_recipe_ids:
            # This recipe has already been rated by the user
            continue
        nb_ingredients = recipe.ingredients.count()
        if nb_ingredients <= 3:
            # Product/recipe
            continue

        potential_recipes[recipe.id] = recipe

    if len(potential_recipes) == 0:
        return None

    return random.choice(list(potential_recipes.values()))