
from rest_framework.decorators  import api_view
from rest_framework.response    import Response
from django.db                  import transaction
from common.decorators          import api_arg, api_check_user_id, api_model_arg

from planning_mgr.models        import Dish, DishRecipe
from planning_mgr.decorators    import user_dishrecipe_decorator, ratio_decorator

from planning_mgr.controller.dish    import factorize_and_order_dishes

from recipe_mgr.models          import Recipe, DishType

from shopping_mgr.models        import ShoppingList

from user_mgr.premium           import ensure_subscription_level

@api_view(['POST'])
@api_check_user_id
@api_model_arg('dish', Dish)
@api_model_arg('recipe', Recipe)
@api_model_arg('dish_type', DishType, allow_none=True)
@api_arg('index', int, 0)
@api_arg('force', bool, False)
@api_arg('validated', bool, False)
@api_arg('ratio', float, None)
@api_arg('update_dish_type', bool, False)
@user_dishrecipe_decorator
@ratio_decorator
# @ensure_subscription_level(1)
@transaction.atomic
def set_dish_recipe(request, user_id, dish, recipe, index, force, validated,
                             existing_dishrecipes, ratio, update_dish_type, dish_type):
    """
    Set one recipe on a dish, on a given index  (0 if there is only one recipe attached to this dish)

    If it's an aggregated dish :
    - splitting the dish into multiples "sub-dishes", keeping ratios and recipes
    - replacing the recipe at "index" by the one given

    @param update_dish_type: if True, allow to change the dishtype if the recipe is not compatible.
    @param dish_type: if update_dish_type, use this dish_type
    """
    if len(existing_dishrecipes) == 0:
        return Response({"error": "cannot set a recipe with no previously existing recipes"}, 400)
    if len(existing_dishrecipes) == 1:
        if index > 0:
            return Response({"error": "setting a dish recipe at index>0 on a simple dish"}, 400)
        dish = dish
        existing_dishrecipes.delete()
    else:
        splitted_dish_type_ids = dish.splitted_dishtype_ids
        if index > len(splitted_dish_type_ids):
            return Response({"error": "index >= number of sub dish types "}, 400)

         # Update dish orders to leave some space to new dishes
        for other_dish in dish.meal_slot.dishes.filter(order__gt=dish.order):
            other_dish.order += len(splitted_dish_type_ids) - 1
            other_dish.save()

        # Splitting this dish into multiple sub-dishes
        existing_dishrecipes = list(existing_dishrecipes)
        original_dish_order = dish.order
        new_dishes = []
        for i, sub_dish_type_id in enumerate(splitted_dish_type_ids):
            if i == 0:
                dish.dish_type_id = sub_dish_type_id
                dish.save()
                new_dish = dish
            else:
                new_dish = Dish.objects.create(meal_slot=dish.meal_slot, dish_type_id = sub_dish_type_id,
                                            order=original_dish_order + i)
                existing_dishrecipes[i].dish = new_dish
                existing_dishrecipes[i].save()
            new_dishes.append(new_dish)

        # Removing the previous dishrecipe
        existing_dishrecipes[index].delete()
        dish = new_dishes[index]

    if update_dish_type:
        if dish_type is None:
            # If the recipe is compatible with the dish, don't change its dish_type
            if recipe.dish_types.filter(pk=dish.dish_type_id).count() == 0:
                # Otherwise, take the first dish type of the recipe
                dish_type = recipe.dish_types.first()
        if dish_type is not None:
            dish.dish_type = dish_type
            dish.save()

    dish_user = None
    if force:
        dish_user = request.user # When forced, the dish recipe is associated to the user

    if ratio <= 0.2:
        raise Exception("Setting invalid dishrecipe ratio : %s for dish %s" % (ratio, dish.pk))

    dish_recipe = DishRecipe.objects.create(dish=dish, ratio=ratio, user=dish_user, order=1,
                                            recipe_id=recipe.id, validated=validated)

    # Deleting recent notnows on this recipe
    request.user.recent_not_nows.filter(recipe=recipe).delete()

    dish = Dish.objects.select_related('dish_type', 'meal_slot__day').get(pk=dish.id)
    if dish.dish_type.monotonous:
        apply_set_recipe_monotony(request.user, dish, recipe)

    return Response({"status": "ok", "dish_recipe_id": dish_recipe.id}, 201)


def apply_set_recipe_monotony(user, dish, recipe):
    """
    After forcing a recipe on a monotonous dish_type, apply to all the dishes of the same dish_type that :
    - don't belong to metaplanning
    - with days non-validated
    - only if dish is not validated or forced
    """
    planning_id = dish.meal_slot.day.planning_id
    dish_recipes = DishRecipe.objects.filter(dish__meal_slot__day__planning_id=planning_id,
                                             dish__dish_type=dish.dish_type,
                                             validated=False,
                                             user=None).\
                                      exclude(dish__meal_slot__day__skipped=False)

    dish_recipes.update(recipe=recipe)

@api_view(['POST'])
@api_check_user_id
@api_model_arg('dish', Dish)
@user_dishrecipe_decorator
@api_model_arg('recipes', Recipe, is_list=True)
@api_arg('force', bool, False)
@api_arg('validated', bool, False)
@api_arg('ratio', float, None)
@ratio_decorator
# @ensure_subscription_level(1)
@transaction.atomic
def set_dish_recipes(request, user_id, dish, existing_dishrecipes, recipes, force, validated, ratio):
    existing_dishrecipes.delete()
    dish_user = None
    if ratio <= 0.2:
        raise Exception("Setting set_dish_recipes ratio : %s" % ratio)
    if force:
        dish_user = request.user # When forced, the dish recipe is associated to the user
    for i, recipe in enumerate(recipes):
        DishRecipe.objects.create(dish=dish, ratio=ratio, user=dish_user, order=i,
                                  recipe=recipe, validated=validated)

    return Response({"status": "ok"}, 201)
