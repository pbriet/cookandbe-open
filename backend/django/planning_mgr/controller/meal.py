
from django.utils               import timezone

from planning_mgr.controller    import MEAL_FULL_PREFETCH
from planning_mgr.models        import Day, MealSlot, Dish, MealSlotEater,\
                                       DishType, DishRecipe
from recipe_mgr.models          import Recipe, Ingredient

import datetime
import copy


def get_next_meal_full_prefetch(user, offset = None):
    if offset is None:
        offset = timezone.now()
    query = MealSlot.objects.filter(day__user_id = user.id, day__date__gte = offset.date(),
                                    suggest = True, meal_place__key="home")\
                            .select_related('day')\
                            .order_by('day__date', 'time').prefetch_related(*MEAL_FULL_PREFETCH)
    if query.count() < 1:
        return None
    # Max time until next displayed meal
    delta_max = timezone.timedelta(seconds = 24 * 3600)
    # Min time to display previous meal
    delta_min = timezone.timedelta(seconds = 2 * 3600)
    for meal in query:
        # Meal full datetime
        meal_dt = timezone.datetime.combine(meal.day.date, meal.time)
        meal_dt = timezone.make_aware(meal_dt, offset.tzinfo)
        if meal_dt < offset - delta_min:
            # This meal was eaten more than 2 hours before offset
            continue
        if meal_dt > offset + delta_max:
            # Nothing found in the next 24h
            return None
        # This meal is in the next 24h
        return meal
    # No planned meal found from today
    return None


def build_meal(new_meal_slot, meta_meal_slot, is_external, main_profile_id=None):
    if main_profile_id is None:
        main_profile_id =  meta_meal_slot.day.user.main_profile_id
    all_dishes_forced = True
    # Ensure the custom recipe is valid, otherwise switch to suggest meal
    nb_custom_ingredients = 0
    for dish in meta_meal_slot.dishes.all():
        if dish.dish_type.name != DishType.DT_CUSTOM:
            continue
        for dr in dish.dishrecipe_set.all():
            nb_custom_ingredients += len(dr.recipe.ingredients.all())
    force_suggest = (nb_custom_ingredients == 0)
    # Selecting dishes added to the planning
    suggested = meta_meal_slot.suggest or is_external or force_suggest
    if suggested:
        dishes = [d for d in meta_meal_slot.dishes.all() if d.dish_type.name != DishType.DT_CUSTOM]
    else:
        dishes = [d for d in meta_meal_slot.dishes.all() if d.dish_type.name == DishType.DT_CUSTOM]
        assert len(dishes) == 1
        assert len(dishes[0].dishrecipe_set.all()) == 1
        assert dishes[0].dishrecipe_set.all()[0].recipe.internal is True
    
    # Copying dishes
    for dish in dishes:
        new_dish = copy.copy(dish)
        new_dish.id = None
        new_dish.meal_slot = new_meal_slot
        new_dish.save()
        dishrecipes = list(dish.dishrecipe_set.all())
        if len(dishrecipes) == 0:
            all_dishes_forced = False
            continue
        for meta_dish_recipe in dishrecipes:
            dish_recipe = create_dish_recipe(meta_dish_recipe, new_dish)
            all_dishes_forced = all_dishes_forced and dish_recipe.user_id is not None and dish_recipe.validated
    # Adding MealSlotEaters
    for meal_slot_eater in meta_meal_slot.meal_slot_eaters.all():
        if (not meta_meal_slot.suggest or is_external) and\
            meal_slot_eater.eater.profile_id != main_profile_id:
            # Custom/external meal, all eaters disabled but main_profile
            continue
        new_meal_slot_eater = copy.copy(meal_slot_eater)
        new_meal_slot_eater.id = None
        new_meal_slot_eater.meal_slot = new_meal_slot
        new_meal_slot_eater.save()
    
    # Updating the "suggest" attribute, according to :
    # - The number of forced dishes (True if every dish is forced)
    # - The content of the custom recipe
    new_meal_slot.suggest = not all_dishes_forced or force_suggest
    new_meal_slot.save()

def create_dish_recipe(meta_dish_recipe, new_dish):
    dish_recipe = DishRecipe.clone(meta_dish_recipe, new_dish)
    if new_dish.dish_type.name == DishType.DT_CUSTOM:
        dish_recipe.recipe = Recipe.clone(meta_dish_recipe.recipe)
        dish_recipe.save()
    return dish_recipe
