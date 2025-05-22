
from django.db                  import transaction

from rest_framework.decorators  import api_view
from rest_framework.response    import Response

from common.date                import today
from common.decorators          import api_arg, api_check_user_id, api_model_arg

from planning_mgr.controller.dish   import factorize_and_order_dishes, delete_mealslot_dish
from planning_mgr.decorators    import user_dishrecipe_decorator, day_from_date_decorator
from planning_mgr.models        import Day, MealSlot, Dish,\
                                       DishRecipe, NotNow


from recipe_mgr.models          import Recipe

from shopping_mgr.models        import ShoppingList

from django.db                  import transaction

import datetime

@api_view(['POST'])
@api_check_user_id
@day_from_date_decorator('date')
@api_arg('value', bool)  # False == set as skipped !
def day_force_as_filled(request, user_id, day, value):
    """
    Set a day as being filled  (skipped = False)
    Returns if the day is currently in a shopping_list or not
    """
    if day.shopping_list_id is not None:
        return Response({"error": "this day has been added to a shopping list therefore can't be modified"}, 400)
    day.skipped = not value
    day.save()
    return Response({"status": "success", "skipped": day.skipped})

@api_view(['POST'])
@api_check_user_id
@api_model_arg('dish', Dish)
@user_dishrecipe_decorator
@api_arg('recipe_id', int)
@transaction.atomic
def validate_dish(request, user_id, dish, existing_dishrecipes, recipe_id):
    """
    Set a dishrecipe as validated
    If dishtype is simple, that's just it.

    Otherwise, split the dish in 2. If not, the other dishrecipes won't be mutable in hippocrate
    """
    for i_recipe, dr in enumerate(existing_dishrecipes):
        if dr.recipe_id == recipe_id:
            dr.validated = True
            dr.save()
            break
    else:
        return Response({"error": "no such recipe for this dish"}, status=400)
    if len(existing_dishrecipes) > 1:
        original_dish_order = dish.order
        # Complex dish type -> let's split it
        dish_type_ids = dish.splitted_dishtype_ids

        # Update dish orders to leave some space to new dishes
        for other_dish in dish.meal_slot.dishes.filter(order__gt=dish.order):
            other_dish.order += len(dish_type_ids) - 1
            other_dish.save()

        for i_dish_type, dish_type_id in enumerate(dish_type_ids):
            if i_dish_type == i_recipe:
                # Update current dish type to the sub dish type represented by the recipe
                dish.dish_type_id = dish_type_id
                dish.order = original_dish_order + i_dish_type
                dish.save()
            else:
                # Create another dish, and binding the dishrecipe to it
                new_dish = Dish.objects.create(meal_slot=dish.meal_slot, dish_type_id = dish_type_id,
                                               order=original_dish_order + i_dish_type, optional=False)
                existing_dishrecipes[i_dish_type].dish = new_dish
                existing_dishrecipes[i_dish_type].save()

    return Response({"status": "success", "has_modified_structure": len(existing_dishrecipes) > 1})


@api_view(['POST'])
@api_check_user_id
@api_model_arg('recipe', Recipe)
@api_model_arg('dish', Dish, allow_none=True)
@transaction.atomic
def not_now(request, user_id, recipe, dish):
    """
    Adds a NotNow object in the database
    @param dish: if given, will unlock the dishrecipes on this dish with the given recipe
    """
    if recipe.internal:
        return Response({"error": "internal recipes can't be automatically replaced"}, 400)
    if dish:
        # Unlocking dishrecipes on the given dish even if they are validated
        DishRecipe.objects.filter(recipe = recipe, dish=dish).update(user=None, validated=False)
    obj = NotNow.objects.create(user_id=user_id, recipe=recipe)
    return Response({"status": "ok"}, 201)


@api_view(['POST'])
@api_check_user_id
@api_arg('meal_slot_id', int)
@api_arg('dish_type_id', int)
@api_arg('replace_optional_if_empty', bool, True)
@transaction.atomic
def add_dish(request, user_id, meal_slot_id, dish_type_id, replace_optional_if_empty):
    """
    Add a dish in a given meal_slot
    @param replace_optional_if_empty: if there is already a dish with this dish type, that is optional and without
                                      dishrecipes, replace the optional one by the new one
    """
    try:
        meal_slot = MealSlot.objects.select_related('day').get(pk=meal_slot_id)
    except MealSlot.DoesNotExist:
        return Response({"error": "no such mealslot"}, 400)
    if meal_slot.day.user_id != user_id:
        return Response({"error": "this mealslot doesn't belong to you !"}, 400)
    # Disable add dishes on non suggested meal_slots
    if not meal_slot.suggest or meal_slot.is_external:
        return Response({"error": "this mealslot is not suggested or external"}, 400)
    replacing = False
    if replace_optional_if_empty:
        optional_dishes = list(Dish.objects.filter(meal_slot=meal_slot, dish_type_id=dish_type_id,
                                                   optional=True, dishrecipe=None))
        if len(optional_dishes):
            # Setting the optional dish as mandatory
            optional_dishes[0].optional = False
            optional_dishes[0].save()
            replacing = True

    if not replacing:
        # Creating a new dish
        Dish.objects.create(meal_slot=meal_slot, dish_type_id=dish_type_id, optional=False, order=1)
    factorize_and_order_dishes(meal_slot)
    return Response({"status": "ok"}, 201)

@api_view(['POST'])
@api_check_user_id
@api_arg('dish_id', int)
@api_arg('dish_type_id', int, None)
@transaction.atomic
def delete_dish(request, user_id, dish_id, dish_type_id):
    """
    In a planning, removes a dish, of a part of a dish (if aggregated dishtype)
    """
    try:
        dish = Dish.objects.select_related('dish_type', 'meal_slot__day').get(pk=dish_id)
    except Dish.DoesNotExist:
        return Response({"error": "no such dish"}, 400)
    if dish.meal_slot.day.user_id != user_id:
        return Response({"error": "this dish doesn't belong to you !"}, 400)
    if dish_type_id is not None and dish_type_id != dish.dish_type_id and\
                                    dish_type_id not in dish.splitted_dishtype_ids:
        return Response({"error": "invalid dishtype id"}, 400)
    delete_mealslot_dish(dish, dish_type_id)
    return Response({"status": "deleted"})


@api_view(['POST'])
@api_check_user_id
@api_model_arg('dish', Dish)
@user_dishrecipe_decorator
@transaction.atomic
def invalidate_dish_content(request, user_id, dish, existing_dishrecipes):
    """
    Set DishRecipes associated to the dish as being not validated
    """
    for dr in existing_dishrecipes:
        dr.validated = False # Not validated by the user
        dr.user = None  # If it was by forced by the user, it is not anymore
        dr.save()

    return Response({"status" : "ok"}, 200)



@api_view(['POST'])
@api_check_user_id
@api_model_arg('dish', Dish)
def toggle_dish_activation(request, user_id, dish):
    dish.activated = not dish.activated
    dish.save()
    return Response({"status" : "ok"}, 200)

@api_view(['POST'])
@api_check_user_id
@api_model_arg('dish', Dish)
@api_model_arg('recipe', Recipe)
def toggle_dishrecipe_shopping(request, user_id, dish, recipe):
    dishrecipe = dish.dishrecipe_set.get(recipe=recipe)
    dishrecipe.in_shopping_list = not dishrecipe.in_shopping_list
    dishrecipe.save()
    return Response({"status" : "ok"}, 200)
