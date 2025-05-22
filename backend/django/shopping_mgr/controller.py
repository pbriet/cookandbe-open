from collections            import defaultdict

from planning_mgr.models    import Day, DishRecipe

from shopping_mgr.models    import ShoppingItem

def get_shopping_days(shopping_list, updateDays = False, keepSkipped = False):
    days = Day.objects.filter(
        user = shopping_list.user,
        date__gte = shopping_list.start_date,
        date__lte = shopping_list.end_date,
    )
    if updateDays:
        # Bind each day to this shopping_list, even the non-planified ones
        # The can't be modified once it's done.
        days.update(shopping_list = shopping_list)
    if not keepSkipped:
        # Now, keep only the validated one to fill the list with items
        days = days.filter(skipped = False)
    return days

def get_shopping_dish_recipes(day_ids, prefetch = tuple()):
    dish_recipes = DishRecipe.objects.filter(dish__meal_slot__day_id__in = day_ids)\
        .exclude(dish__meal_slot__meal_place__key = "away")\
        .exclude(in_shopping_list=False)\
        .prefetch_related(*prefetch)
    return dish_recipes

def fill_shopping_list(shopping_list):
    """
    Given an empty shopping list, fill it with the recipes contained in the planned days
    """
    items               = []                # All items
    is_stored           = set()             # All stored food ids
    entries             = defaultdict(int)  # (date, food_id, raw_state_id) -> grams
    day_ids             = [d.id for d in get_shopping_days(shopping_list, updateDays=True, keepSkipped=False)]
    dish_recipes        = get_shopping_dish_recipes(day_ids, prefetch = ('recipe__ingredients__food__type', ))

    # Aggregating ingredients in ShoppingItems
    for dish_recipe in dish_recipes:
        for ingredient in dish_recipe.recipe.ingredients.all():
            ingredient_grams = ingredient.grams_without_loss * dish_recipe.ratio
            if ingredient.food.type.usually_stored:
                is_stored.add(ingredient.food_id)
            entries[(ingredient.food_id, ingredient.raw_state_id)] += ingredient_grams

    # Creating ShoppingItems in RAM
    for keys, grams in entries.items():
        food_id, raw_state_id = keys
        items.append(ShoppingItem(
            food_id=food_id,
            raw_state_id=raw_state_id,
            grams=grams,
            got_it=food_id in is_stored,
            shopping_list=shopping_list,
        ))

    # Optimization : creating all items at once in database
    ShoppingItem.objects.bulk_create(items)
