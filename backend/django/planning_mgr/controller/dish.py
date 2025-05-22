
from common.model               import reload_object

from planning_mgr.models        import Dish
from recipe_mgr.helpers         import detect_aggregations


def delete_mealslot_dish(dish, dish_type_id=None, meal_slot=None):
    """
    Removes a dish in a mealslot, or part of a dish (if dish type aggregated)
    """
    if meal_slot is None:
        meal_slot = dish.meal_slot
    if dish_type_id is None or dish.dish_type_id == dish_type_id:
        # Just deleting the dish
        dish.delete()
    else:
        splitted_dishtype_ids = dish.splitted_dishtype_ids
        assert dish_type_id in splitted_dishtype_ids
        # From aggregated dishtype to non-aggregated dishtype
        # Creating new dishes with all the subtypes except the one disabled
        for sub_dt_id in splitted_dishtype_ids:
            if sub_dt_id != dish_type_id :
                Dish.objects.create(meal_slot=meal_slot, order=1, dish_type_id=sub_dt_id)
        dish.delete()
        reload_object(meal_slot)
        factorize_and_order_dishes(meal_slot)

def factorize_and_order_dishes(meal_slot):
    """
    Within a meal_slot, update the order of dishes accordingly to the MealDishOption order,
    and factorize dishes that should be aggregated
    """
    dish_options = list(meal_slot.meal_type.dish_options.order_by('id'))
    ordered_dish_type_ids = [dish_option.dish_type_id for dish_option in dish_options]
    
    dish_by_dish_type = {}
    for dish in meal_slot.dishes.prefetch_related('dishrecipe_set'):
        dish_by_dish_type[dish.dish_type_id] = dish

    # Order of the dish
    existing_dishtype_ids = []
    sorted_dish_ids = set()
    i_order = 0
    for dish_type_id in ordered_dish_type_ids:
        dish = dish_by_dish_type.get(dish_type_id, None)
        if dish is None or dish.id in sorted_dish_ids:
            continue # No such dish type in the meal
        existing_dishtype_ids.append(dish_type_id)
        
        dish.order = i_order
        dish.save()
        sorted_dish_ids.add(dish.id)
        i_order += 1

    # Applying aggregations by merging multiple dishes into one with multiple elements
    for master_dish_type_id, sub_dish_type_ids in detect_aggregations(existing_dishtype_ids).items():
        sub_dish_type_ids = sorted(sub_dish_type_ids)

        # We only keep the first dish, and set it as aggregated
        main_dish = dish_by_dish_type[sub_dish_type_ids[0]]
        main_dish.dish_type_id = master_dish_type_id
        main_dish.save()

        # We delete the other dishes
        for i in range(1, len(sub_dish_type_ids)):
            other_dish = dish_by_dish_type.pop(sub_dish_type_ids[i])
            for dish_recipe in other_dish.dishrecipe_set.all():
                dish_recipe.dish_id = main_dish.id
                dish_recipe.order = i + 1
                dish_recipe.save()
            other_dish.delete()
