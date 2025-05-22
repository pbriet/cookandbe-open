from collections                import defaultdict

from django.core.exceptions     import PermissionDenied
from django.db                  import transaction

import datetime

from rest_framework.decorators  import api_view
from rest_framework.response    import Response
from rest_framework.views       import APIView

from common.decorators          import api_arg, api_check_user_id, api_model_arg
from common.math                import round_to_closest, round_to_closest_ratio

from eater_mgr.decorators       import eater_decorator
from eater_mgr.ratios           import RatiosCalculator

from planning_mgr.controller.meta   import build_mealslot_from_meta, get_meta_mealslot

from planning_mgr.decorators    import meal_slot_decorator, day_from_date_decorator
from planning_mgr.models        import MealSlot, MealSlotEater, DishRecipe, Day, MealType, MealPlace
from planning_mgr.serializers   import MealSlotLightSerializer, MealTypeSerializer, MealPlaceSerializer, MealTypeLightSerializer

from recipe_mgr.models          import FoodType

from user_mgr.premium           import ensure_subscription_level

def prefetch_day_eaters_dishes(day_id):
    """
    Returns a day with its mealslots, dishes, dishrecipes and eaters
    """
    return Day.objects.prefetch_related('meal_slots__eaters', 'meal_slots__dishes__dishrecipe_set').get(pk=day_id)

class MealSlotView(APIView):
    def get(self, request, **kargs):
        meal_slot_id = self.kwargs['meal_slot_id']
        meal_slot = MealSlot.objects.get(pk=meal_slot_id)
        if meal_slot.day.user != request.user:
            raise PermissionDenied
        return Response(MealSlotLightSerializer.serialize(meal_slot))

@api_view(['POST'])
@meal_slot_decorator
@api_arg('speed', int, validators=MealSlot.SPEED_VALIDATORS)
def set_mealslot_speed(request, meal_slot, speed):
    previous_value = meal_slot.speed
    meal_slot.speed = speed
    meal_slot.save()
    return Response({"status": "ok", "previous_value": previous_value})



def update_ratios_decorator(mode):
    """
    Handle update of DishRecipes ratio on a given meal when
    adding/removing a eater
    """
    def decorator(fcn):
        def new_fcn(request, meal_slot, eater):

            meal_slot = MealSlot.objects.prefetch_related('eaters', 'dishes__dishrecipe_set').get(pk=meal_slot.id)

            ratio_calculator = RatiosCalculator(request.user)

            # Eaters before any modifications
            eaters_before = meal_slot.eaters.all()

            # Total ratio of eater profiles
            profile_ratios = ratio_calculator.profile_ratios
            total_eaters_ratio_before = sum(profile_ratios[eater.profile_id] for eater in eaters_before)

            # How much this eater represents comparing to total
            profile_ratio_perc = profile_ratios[eater.profile_id] / total_eaters_ratio_before

            ### Calling original function
            res = fcn(request, meal_slot, eater)
            if res.data['status'] != 'ok':
                return res

            if mode == "remove":
                nb_new_eaters = len(eaters_before) - 1
            else:
                nb_new_eaters = len(eaters_before) + 1
            precision = ratio_calculator.precision_from_nb_eaters(nb_new_eaters)

            # Updating ratios by adding/removing eater
            for dish in meal_slot.dishes.all():
                for dish_recipe in dish.dishrecipe_set.all():
                    if mode == "remove":
                        # Removing the percentage this eater was representing, and rounding to closest 0.5
                        dish_recipe.ratio = round_to_closest_ratio(dish_recipe.ratio * (1 - profile_ratio_perc), precision)
                    else:
                        dish_recipe.ratio = round_to_closest_ratio(dish_recipe.ratio * (1 + profile_ratio_perc), precision)

                    if dish_recipe.ratio <= 0.2:
                        raise Exception("Setting dish recipe ratio after adding/removing eater : %s" % dish_recipe.ratio)
                    dish_recipe.save()

            return res
        new_fcn.__name__ = fcn.__name__
        return new_fcn
    return decorator

@api_view(['POST'])
@api_arg('eater_id', int)
@meal_slot_decorator
@eater_decorator
@update_ratios_decorator('add')
def add_mealslot_eater(request, meal_slot, eater):
    if eater in meal_slot.eaters.all():
        return Response({"status": "already set"})
    if meal_slot.suggest is False:
        return Response({"status": "can't add eaters to a custom meal"}, 400)

    # Adding the eater
    MealSlotEater.objects.create(meal_slot=meal_slot, eater=eater)

    return Response({"status": "ok"})

@api_view(['POST'])
@api_arg('eater_id', int)
@meal_slot_decorator
@eater_decorator
@update_ratios_decorator('remove')
def remove_mealslot_eater(request, meal_slot, eater):
    if eater not in meal_slot.eaters.all():
        return Response({"status": "already removed"})
    if eater.profile == request.user.main_profile:
        return Response({"status": "can't remove main profile"}, 400)

    # Removing the eater
    MealSlotEater.objects.filter(meal_slot=meal_slot, eater=eater).delete()

    return Response({"status": "ok"})

@api_view(['POST'])
@day_from_date_decorator('date')
@api_model_arg('meal_type', MealType)
@api_model_arg('meal_place', MealPlace, id_arg_name="meal_place_key", pk_name="key", pk_type=str)
@api_check_user_id
# @ensure_subscription_level(1)
@transaction.atomic
def set_meal_place(request, user_id, day, meal_type, meal_place):
    """
    For a given date, set a meal_place on a meal_type.
    Create/replace/delete the existing meal_slot with a default one
    """
    existing_mealslot = None
    try:
        existing_mealslot = day.meal_slots.get(meal_type=meal_type)
    except MealSlot.DoesNotExist:
        pass

    if (existing_mealslot and existing_mealslot.meal_place_id == meal_place.id) or\
       (not existing_mealslot and meal_place.key == "donoteat"):
        return Response({"status": "no change"}, 200)

    # Retrieve the metaplanning mealslot for this day and meal_type
    meta_mealslot = get_meta_mealslot(meal_type, day, request.user)

    # Deleting the existing mealslot : we'll replace it by a default one
    if existing_mealslot:
        existing_mealslot.delete()

    # Create a new mealslot from default metaplanning mealslot
    build_mealslot_from_meta(meta_mealslot, day, meal_place=meal_place)

    return Response({"status": "done"})

@api_view(['GET'])
@api_arg('date', datetime.date)
@api_check_user_id
def day_structure(request, user_id, date):
    """
    Returns for a given day the list of each meal_type, if there is a mealslot or not, and with which speed/eaters
    """
    day = Day.objects.prefetch_related('meal_slots__eaters', 'meal_slots__meal_place', 'meal_slots__meal_type')
    day = day.get(date=date, user=request.user)

    meal_slots = day.meal_slots.all()
    meal_slot_per_meal_type = dict((meal_slot.meal_type_id, meal_slot) for meal_slot in meal_slots)

    meal_types = sorted(MealType.objects.all(), key=lambda x: x.id)
    not_eating = MealPlace.objects.get(key="donoteat")

    res = []

    for meal_type in meal_types:
        meal_type_data = {'meal_type': MealTypeLightSerializer(meal_type).data}
        meal_slot = meal_slot_per_meal_type.get(meal_type.id)
        if meal_slot is None:
            meal_type_data['meal_place'] = MealPlaceSerializer(not_eating).data
        else:
            meal_type_data['meal_slot_id'] = meal_slot.id
            meal_type_data['suggest'] = meal_slot.suggest
            meal_type_data['meal_place'] = MealPlaceSerializer(meal_slot.meal_place).data
            if meal_slot.is_cooked:
                meal_type_data['speed'] = meal_slot.speed
            if not meal_slot.is_external:
                meal_type_data['eater_ids'] = [eater.profile_id for eater in meal_slot.eaters.all()]

        res.append(meal_type_data)

    return Response({"structure": res})



# Grouping categories together
FOOD_TYPE_RENAMING = {"Pâtisseries et biscuits" :    "Dessert",
                      "Biscuits secs sucrés" :       "Dessert",
                      "Confiseries non chocolatées": "Dessert",
                      "Entremets et glaces": "Dessert",
                      "Confitures": "Dessert",
                      "Sucres et confiseries": "Dessert",
                      "Préparations pour pâtisseries": "Dessert",
                      "Chocolats et produits à base de chocolat": "Dessert",
                      "Sucres, miels, sirops": "Dessert",
                      "Viennoiseries et brioches": "Dessert",
                      "Biscuits salés apéritifs" :"Apéritif/Crackers",
                      "Produits laitiers et entremets": "Produits laitiers",
                      "Succédanés du lait": "Produits laitiers",
                      "Desserts lactés frais ou UHT": "Produits laitiers",
                      "Laits": "Produits laitiers",
                      "Aliments lactés diététiques": "Produits laitiers",
                      "Crèmes et spécialités à base de crème": "Produits laitiers",
                      "Yaourts et spécialités laitières type yaourts": "Produits laitiers",
                      "Fromages blancs ultrafrais": "Produits laitiers",
                      "Fromages affinés à pâte molle": "Fromage",
                      "Fromages affinés à pâte persillée": "Fromage",
                      "Fromages affinés à pâte dure": "Fromage",
                      "Fromages": "Fromage",
                      "Fromages affinés à pâte ferme": "Fromage",
                      "Fromages fondus": "Fromage",
                      "Fromages non affinés et spécialités fromagères": "Fromage",
                      "Plats à base de fromage": "Fromage",
                      "Poissons et batraciens non transformés": "Poisson",
                      "Poissons et batraciens": "Poisson",
                      "Produits à base de poissons": "Poisson",
                      "Plats à base de poisson ou produits aquatiques": "Poisson",
                      "Crustacés et mollusques": "Fruits de mer",
                      "Crustacés et mollusques non transformés": "Fruits de mer",
                      "Produits à base de crustacés et mollusques": "Fruits de mer",
                      "Soupes et bouillons": "Soupe",
                      "Soupes prêtes à consommer": "Soupe",
                      "Soupes et bouillons non reconstitués": "Soupe",
                      "Bouillons prêts à consommer": "Soupe",
                      "Oeufs et dérivés": "Oeufs",
                      "Volailles": "Viandes",
                      "Abats": "Viandes",
                      "Plats à base de viande ou volaille": "Viandes",
                      "Charcuteries et salaisons": "Charcuterie",
                      "Pommes de terre et apparentés": "Pommes de terre",
                      "Jus et nectars": "Fruits",
                      "Salades composées et crudités": "Légumes",
                      "Plats à base de légumes ou légumineuses": "Légumes",
                      "Biscottes et pains non levés": "Pains",
                      "Pâtes et semoules": "Céréales",
                      "Riz et autres graines": "Céréales",
                      "Farines et amidons": "Céréales",
                      "Céréales et pâtes": "Céréales",
                      "Plats à base de céréales ou pâtes": "Céréales"}



@api_view(['GET'])
@meal_slot_decorator
def external_meal_suggestions(request, meal_slot):
    if meal_slot.meal_place.key != "away":
        return Response({"error": "this is not an external meal"}, 400)

    # Food type name -> grams
    food_type_grams = defaultdict(float)

    dish_recipes = DishRecipe.objects.filter(dish__meal_slot=meal_slot).\
                                      select_related('recipe').prefetch_related('recipe__ingredients__food__type')
    for dishrecipe in dish_recipes:
        for ingredient in dishrecipe.recipe.ingredients.all():
            food_type_grams[ingredient.food.type.name] += ingredient.grams * dishrecipe.ratio

    for key in list(food_type_grams.keys()):
        new_key = FOOD_TYPE_RENAMING.get(key, None)
        if new_key is None:
            continue
        food_type_grams[new_key] += food_type_grams[key]
        del food_type_grams[key]

    if "Eaux" in food_type_grams:
        del food_type_grams["Eaux"]


    res = []
    for ft_name, grams in sorted(food_type_grams.items(), key=lambda x: x[1], reverse=True):
        if grams < 30:
            continue
        # Rounding grams to the closest 10g
        grams = round_to_closest(grams, 10)
        res.append({"name": ft_name, "grams": grams})

    return Response({"result": res}, 200)
