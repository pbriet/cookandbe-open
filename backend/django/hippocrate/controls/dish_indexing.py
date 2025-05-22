from hippocrate_cpp.core                import create_cpp_dish, create_cpp_dish_element


def cpp_dish_from_dish(dish, meal_slot=None, initial_ratio=None):
    """
    From a dish, creates a C++ dish with its elements and ratios
    @param meal_slot: optionally, the parent mealslot
    """
    if meal_slot is None:
        meal_slot = dish.meal_slot
     # Création du dish
    cpp_dish = create_cpp_dish(dish.id, meal_slot.day_id, meal_slot.id, meal_slot.meal_type_id, dish.dish_type_id, dish.optional, meal_slot.is_external)
    if initial_ratio is not None:
        cpp_dish.set_initial_ratio(initial_ratio)
    for eater in meal_slot.eaters.all():
        cpp_dish.add_eater_profile(eater.profile.id)
    # Création de dish elements en splittant les dish types aggrégés
    for dish_type_id in sorted(dish.splitted_dishtype_ids):
        cpp_element = create_cpp_dish_element(dish_type_id)
        # DishRecipeFilters and DishFoodFilters are not used for the moment. Uncomment the following lines to activate them
        #for recipe_filter in filter(lambda x: x.dish_type_id == dish_type_id, dish.dish_recipe_filters.all()):
            #cpp_element.add_recipe_tag(recipe_filter.recipe_tag_id)
        #for food_filter in filter(lambda x: x.dish_type_id == dish_type_id, dish.dish_food_filters.all()):
            #cpp_element.add_food_tag(food_filter.food_tag_id)
        cpp_dish.add_element(cpp_element)
    return cpp_dish
