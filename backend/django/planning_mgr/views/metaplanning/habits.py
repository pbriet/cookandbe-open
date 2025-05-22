
from rest_framework.decorators          import api_view
from rest_framework.response            import Response

from common.decorators                  import api_arg, api_check_user_id, api_model_arg
from common.model                       import reload_object

from planning_mgr.models                import MealSlot, Dish, DishRecipe, MealType
from planning_mgr.serializers           import MealSlotHabitSerializer

from planning_mgr.controller.dish       import factorize_and_order_dishes, delete_mealslot_dish

from recipe_mgr.models                  import Recipe, DishType

from optalim.log import logger

META_MEALSLOT_PREFETCH = ('dishes__dishrecipe_set__recipe',
                          'meal_type__dish_options__default_recipe',
                          'meal_type__dish_options__dish_type',
                          'meal_place')

def get_meta_mealslots(user, meal_type, *prefetch_related):
    return list(MealSlot.objects.prefetch_related(*prefetch_related).filter(
                            meal_type=meal_type,
                            day__in=user.meta_planning.days.all()))

def prefetch_firstday_mealslot(user, meal_type):
    """
    Returns a prefetched mealslot : of the given meal_type on the user metaplanning, on one random day
    """
    return user.meta_planning.days.first().meal_slots.prefetch_related(
                 *META_MEALSLOT_PREFETCH).filter(meal_type=meal_type)[0]


@api_view(['GET'])
@api_check_user_id
@api_model_arg('meal_type', MealType)
def mealtype_habits(request, user_id, meal_type):
    """
    Returns the habits for this meal_type
    """
    meal_slot = prefetch_firstday_mealslot(request.user, meal_type)

    return Response(MealSlotHabitSerializer.serialize(meal_slot), status=200)


@api_view(['GET'])
@api_check_user_id
@api_arg('enabled_only', bool, True)
def all_mealtypes_habits(request, user_id, enabled_only):
    """
    Returns the habits for every meal_types
    """
    res = []
    for meal_type in MealType.objects.all().order_by('id'):
        meal_slots = list(get_meta_mealslots(request.user, meal_type, *META_MEALSLOT_PREFETCH))
        if enabled_only:
            # Checking that at least one day of the week, this mealslot is taken at home
            sometimes_at_home = False
            for meal_slot in meal_slots:
                if meal_slot.meal_place.key in ("home", "lunchpack"):
                    # Skipping meal that is not taken at home
                    sometimes_at_home = True
                    break
            if not sometimes_at_home:
                continue # Skipping
        res.append(
            {'meal_type': {'id': meal_type.id, 'name': meal_type.name},
             'habits': MealSlotHabitSerializer.serialize(meal_slots[0])})

    return Response({'content': res}, status=200)


@api_view(['POST'])
@api_check_user_id
@api_model_arg('meal_type', MealType)
@api_arg('suggest', bool)
def set_mealtype_suggest(request, user_id, meal_type, suggest):
    """
    Switch "suggestion mode" to 'suggest' or 'static', depending on previous status.
    If switching to 'suggest', initialize default suggestion.
    If switching to 'static', initialize default dishes and forced dishrecipes
    """
    meal_slots = get_meta_mealslots(request.user, meal_type, *META_MEALSLOT_PREFETCH)
    for meal_slot in meal_slots:
        if meal_slot.suggest == suggest:
            continue
        custom_dishes = meal_slot.dishes.filter(dish_type__name = DishType.DT_CUSTOM)
        if custom_dishes.count() != 1 or custom_dishes[0].recipes.count() != 1:
            return Response({"error" : "suggest switch failed"}, status = 400)
        assert custom_dishes[0].recipes.all()[0].internal is True
        meal_slot.suggest = suggest
        meal_slot.save()
    request.user.meta_planning.set_modified()
    return Response({"status": "ok", "suggest": suggest}, status=201)

@api_view(['POST'])
@api_check_user_id
@api_model_arg('meal_type', MealType)
@api_model_arg('recipe', Recipe)
def del_mealtype_static_recipe(request, user_id, meal_type, recipe):
    """
    <should be called only if this meal_type is in 'static' mode  (suggest = False)>
    Remove a recipe (and its dish) from the default mealslot
    """
    logger.warning("DEPRECATED: del_mealtype_static_recipe function (api/user/*/meal_type/*/del_static_recipe) should no longer be used. Please use a custom recipe instead.")
    meal_slots = get_meta_mealslots(request.user, meal_type, 'dishes__dishrecipe_set')
    for meal_slot in meal_slots:
        assert not meal_slot.suggest, "calling del_mealtype_static_recipe with suggest enabled"
        for dish in meal_slot.dishes.all():
            dishrecipes = list(dish.dishrecipe_set.all())
            if len(dishrecipes) == 1 and dishrecipes[0].recipe_id == recipe.id:
                dish.delete()
                break
        else:
            assert False, "recipe not found in meal_slot"
    request.user.meta_planning.set_modified()
    return Response({"status": "deleted"}, status=201)


@api_view(['POST'])
@api_check_user_id
@api_model_arg('meal_type', MealType)
@api_model_arg('recipe', Recipe)
def add_mealtype_static_recipe(request, user_id, meal_type, recipe):
    """
    <should be called only if this meal_type is in 'static' mode  (suggest = False)>
    Add a recipe (with its dish) in the default mealslot
    """
    logger.warning("DEPRECATED: add_mealtype_static_recipe function (api/user/*/meal_type/*/add_static_recipe) should no longer be used. Please use a custom recipe instead.")
    meal_slots = get_meta_mealslots(request.user, meal_type)
    for meal_slot in meal_slots:
        assert not meal_slot.suggest, "calling add_mealtype_static_recipe with suggest enabled"
        dish = Dish.objects.create(meal_slot = meal_slot, order = 1,
                                   dish_type = recipe.dish_types.first(), optional = False)
        DishRecipe.objects.create(dish=dish, recipe=recipe, ratio=1,
                                   order=1, user=request.user, validated=True)
    request.user.meta_planning.set_modified()
    return Response({"status": "added"}, status=201)

@api_view(['POST'])
@api_check_user_id
@api_model_arg('meal_type', MealType)
@api_model_arg('dish_type', DishType)
def enable_meal_dish(request, user_id, meal_type, dish_type):
    """
    <should be called only if this meal_type is in 'suggest' mode  (suggest = True)>
    Creates a default dish in every meal of one given type
    """
    meta_planning = request.user.meta_planning

    dish_option = meal_type.dish_options.get(dish_type=dish_type)

    for day in meta_planning.days.all():
        for meal_slot in day.meal_slots.prefetch_related("dishes__dish_type").filter(meal_type=meal_type):
            assert meal_slot.suggest, "enable_meal_dish on non-suggested meal_slot"
            existing_dish_types = set(dish.dish_type_id for dish in meal_slot.dishes.all())
            if dish_type.id in existing_dish_types:
                continue # The dish type is already enabled withing this meal_slot
            dish = Dish.objects.create(meal_slot=meal_slot, order=1, dish_type_id=dish_type.id, optional = dish_option.default_optional)
            reload_object(meal_slot)
            factorize_and_order_dishes(meal_slot)

    meta_planning.set_modified()
    return Response({"status": "enabled"})

@api_view(['POST'])
@api_check_user_id
@api_arg('meal_type_id', int)
@api_arg('dish_type_id', int)
def disable_meal_dish(request, user_id, dish_type_id, meal_type_id):
    """
    <should be called only if this meal_type is in 'suggest' mode  (suggest = True)>
    In the metaplanning :
    Deletes all dishes of a given dish_type_id within meals of a given meal_type_id
    """
    disabled = False
    meta_planning = request.user.meta_planning

    for day in meta_planning.days.all():
        for meal_slot in day.meal_slots.prefetch_related("dishes__dish_type").filter(meal_type_id=meal_type_id):
            assert meal_slot.suggest, "disable_meal_dish on non-suggested meal_slot"
            for dish in list(meal_slot.dishes.all()):
                if dish_type_id == dish.dish_type_id:
                    delete_mealslot_dish(dish, dish_type_id, meal_slot=meal_slot)
                    disabled = True

    if not disabled:
        return Response({"status": "error", "message": "no such dish_type in this meal"}, 400)

    meta_planning.set_modified()
    return Response({"status": "disabled"})

@api_view(['POST'])
@api_check_user_id
@api_arg('meal_type_id', int)
@api_arg('dish_type_id', int)
@api_arg('forced_recipe_id', int, -1)
def force_mealtype_dishrecipe(request, user_id, meal_type_id, dish_type_id, forced_recipe_id):
    """
    <should be called only if this meal_type is in 'suggest' mode  (suggest = True)>
    Modifies the structure of one dish within a meal  (forced recipe, recipe tags, food tags)
    """
    forced = False
    meta_planning = request.user.meta_planning

    for day in meta_planning.days.all():
        for meal_slot in day.meal_slots.prefetch_related("dishes__dish_type").filter(meal_type_id=meal_type_id):
            assert meal_slot.suggest, "force_mealtype_dishrecipe on non-suggested meal_slot"
            for dish in meal_slot.dishes.all():
                if dish.dish_type_id != dish_type_id:
                    continue
                if len(dish.splitted_dishtype_ids) > 1:
                    # Cannot force a recipe with a multi-elements dish
                    return Response({"status": "error", "message": "cannot force an aggregated dishtype"}, 400)
                forced = True
                # Cleaning the previous forced recipes (if so)
                dish.dishrecipe_set.all().delete()
                if forced_recipe_id >= 0 :
                    # FIXME: ratio
                    DishRecipe.objects.create(dish=dish, recipe_id=forced_recipe_id, ratio=1., user=request.user)
                # TODO: handle food tags and recipe tags

    if not forced:
        return Response({"status": "error", "message": "no such dish_type in this meal"}, 400)

    meta_planning.set_modified()
    return Response({"status": "updated"})
