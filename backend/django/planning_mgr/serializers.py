from rest_framework                 import serializers, fields

from common.date                    import today

from eater_mgr.ratios               import RatiosCalculator

from hippocrate.controls.filters    import get_disabled_filters_human_readable
from hippocrate.models.recipestorage import MainRecipeStorage

from nutrient.models                import Nutrient

from planning_mgr.controller.planning   import days_shopping_listable
from planning_mgr.models            import MealSlot, Dish, MetaPlanning, MealType, MealPlace, Day

from recipe_mgr.helpers             import detect_aggregations
from recipe_mgr.models              import DishType
from recipe_mgr.serializers         import QuickRecipeSerializer, RatioRecipeSerializer, FullRecipeSerializer

from collections                    import defaultdict


# Dishtypes that cannot be forced in
# the metaplanning
class DynamicDishtypes:
    _values = []

    @classmethod
    def values(cls):
        if len(cls._values) == 0:
            cls._values = [DishType.get_dt(DishType.DT_STARTER).id,
                            DishType.get_dt(DishType.DT_MAIN_COURSE).id,
                            DishType.get_dt(DishType.DT_FULL_COURSE).id,
                            DishType.get_dt(DishType.DT_SIDE).id]
        return cls._values

class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        exclude = []

    recipes = QuickRecipeSerializer(many=True)

class MealSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealSlot
        exclude = []

    dishes = DishSerializer(many=True)

class MealPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlace
        exclude = []

class MealTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealType
        exclude = []

class MealTypeLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealType
        fields = ('id', 'name')

class PlanningMenuSerializer(object):
    """
    Hand-made serializer to translate a planning in a menu-like structure:
    * per day
    * per meal
    * with recipe names
    """
    @staticmethod
    def serialize(days, show_static=False):
        sorted_days = sorted(days, key=lambda x: x.date)
        meal_types = set()
        per_day = []
        for day in sorted_days:
            day_values = {"date": day.date, "meal_slots": {},
                          "shopping_list_id": day.shopping_list_id,
                          "filled": day.is_validated(),
                          "skipped": day.is_skipped()}
            per_day.append(day_values)

            for meal_slot in day.ordered_meal_slots:
                dishes = []
                for dish in sorted(meal_slot.dishes.all(), key=lambda x: x.dish_type_id):
                    dish_recipes = []
                    for dish_recipe in sorted(dish.dishrecipe_set.all(), key=lambda x: x.order):
                        dish_recipes.append({'id': dish_recipe.recipe.id,
                                            'name': dish_recipe.recipe.name,
                                            'photo': dish_recipe.recipe.photo_url,
                                            'ratio': dish_recipe.ratio})

                    dishes.append({"id": dish.id, "recipes": dish_recipes})

                meal_type = meal_slot.meal_type
                if len(dishes) and (meal_slot.suggest or show_static):
                    meal_types.add(meal_type)
                day_values["meal_slots"][meal_type.id] = \
                    {"id": meal_slot.id,
                    "time": meal_slot.time,
                    "external": meal_slot.is_external,
                    "cooked": meal_slot.is_cooked,
                    "place_key": meal_slot.meal_place.key,
                    "suggest": meal_slot.suggest,
                    "dishes": dishes}

        meals = []
        for meal_type in sorted(meal_types, key=lambda x: x.time):
            meals.append({"id" : meal_type.id, "name": meal_type.name})

        return {"start_date": sorted_days[0].date,
                "end_date": sorted_days[-1].date,
                "days": per_day,
                "meal_types": meals}

class DaySuggestionSerializer(object):
    """
    Serializer of one day with suggestions for each dish
    """
    @staticmethod
    def serialize(day, only_dishes=None, user=None):
        suggestions = []
        for meal_slot in day.ordered_meal_slots:
            for dish in meal_slot.ordered_dishes:
                if only_dishes is not None and dish.id not in only_dishes:
                    continue
                splitted_dishtype_ids = dish.splitted_dishtype_ids
                possible_dish_type_ids = sorted(set(splitted_dishtype_ids).union([dish.dish_type_id]))

                # Special case for hippocrate improvements. This is not something from the DB
                if hasattr(dish, 'new_dishrecipe_set'):
                    dish_recipes = dish.new_dishrecipe_set
                else:
                    dish_recipes = sorted(dish.dishrecipe_set.all(), key=lambda x: x.order)

                for i, dish_recipe in enumerate(dish_recipes):
                    if not dish_recipe.validated:
                        # Retrieving the dish_type_id for which the recipe is intended
                        if len(dish_recipes) == 1:
                            dish_type_id = dish.dish_type_id
                        else:
                            dish_type_id = splitted_dishtype_ids[i]
                        dr_dict = {'dish_id': dish.id,
                                   'meal_id': meal_slot.id,
                                   'recipe_id': dish_recipe.recipe_id,
                                   'dish_type_id': dish_type_id,
                                   'ratio': dish_recipe.ratio,
                                   'fully_filtered': dish_recipe.fully_filtered}
                        if not dish_recipe.fully_filtered:
                            dr_dict['disabled_filters'] = get_disabled_filters_human_readable(day, dish_recipe)
                        suggestions.append(dr_dict)
        return {"suggestions": suggestions,
                "shopping_list_id": day.shopping_list_id,
                "metaplanning_changed": day.requires_update(user=user),
                "skipped": day.is_skipped(),
                "validated": day.is_validated(),
                "nb_planned_days": days_shopping_listable(day.user_id).count()}

class DayToFillSerializer(object):
    """
    Serializer of a day currently being filled
    """
    @staticmethod
    def serialize(day, with_ingredients=False):
        has_forced_recipes = False
        res = []
        for meal_slot in day.ordered_meal_slots:
            entry = {"meal_slot": {"id": meal_slot.id,
                                   "meal_type": {"id": meal_slot.meal_type.id, "name": meal_slot.meal_type.name},
                                   "speed": meal_slot.speed,
                                   "meal_place": MealPlaceSerializer(meal_slot.meal_place).data,
                                   "eating": [eater.id for eater in meal_slot.eaters.all()],
                                   "eaten_at_home": meal_slot.meal_place.key == 'home',
                                   "cooked_at_home": meal_slot.meal_place.key in ('home', 'lunchpack')
                                   }
                     }
            if meal_slot.meal_place.key in ("home", "lunchpack"):
                entry["status"] = ("static", "suggested")[meal_slot.suggest]
                entry["dishes"], meal_has_forced_recipes = DayToFillSerializer.serialize_dishes(meal_slot,
                                                                                                with_ingredients=with_ingredients)
                has_forced_recipes = has_forced_recipes or meal_has_forced_recipes
            else:
                # Not at home
                entry["status"] = "away"
            res.append(entry)

        ratios = RatiosCalculator(day.user).get_detailed_ratios_from_bdd([day])

        return {"content": res,
                "ratios": ratios,
                "has_forced_recipes": has_forced_recipes}


    @staticmethod
    def serialize_ingredients(dish_recipe):
        """
        Returns the ingredients of a recipe, with correct ratio
        """
        return RatioRecipeSerializer(dish_recipe.recipe, dish_recipe.ratio,
                                     include_usage=False).data['ingredients']


    @staticmethod
    def serialize_dishes(meal_slot, with_ingredients=False):
        """
        For a suggested meal, returns the serialized dishes
        """
        has_forced_recipes = False
        dishes = []
        for dish in meal_slot.ordered_dishes:
            recipes = []
            # Does one of the existing recipe have the main dishtype of the dish ?
            # If so : don't give details about splitted dishtypes -> it's not possible anymore
            recipes_have_main_dishtype = False
            has_validated_recipes = False
            for dish_recipe in sorted(dish.dishrecipe_set.all(), key=lambda x: x.order):
                recipe_data = MainRecipeStorage.get(dish_recipe.recipe_id)
                recipes.append({"id": dish_recipe.recipe_id, "name": dish_recipe.recipe.name,
                                "ratio": dish_recipe.ratio, "photo": dish_recipe.recipe.photo_url,
                                "price": dish_recipe.recipe.price,
                                "difficulty": dish_recipe.recipe.difficulty,
                                "calories": round(recipe_data.get_data_from_key(Nutrient.NUT_CALORIES, dish_recipe.ratio)),
                                "url_key": dish_recipe.recipe.url_key,
                                "avg_rating": dish_recipe.recipe.avg_rating,
                                "nb_ratings": dish_recipe.recipe.nb_ratings,
                                "in_shopping_list": dish_recipe.in_shopping_list,
                                "validated": dish_recipe.validated})
                if with_ingredients:
                    recipes[-1]["ingredients"] = DayToFillSerializer.serialize_ingredients(dish_recipe)
                has_validated_recipes = has_validated_recipes or dish_recipe.validated
                if dish_recipe.validated and dish.dish_type_id in [d.id for d in dish_recipe.recipe.dish_types.all()]:
                    # There is one validated recipe on main dishtype -> sub dish types are forbidden
                    recipes_have_main_dishtype = True
                # has_forced_recipes == True if there is a forced and validated recipe (user != None) in a suggested meal
                if dish_recipe.user_id is not None and dish_recipe.validated and meal_slot.suggest and not dish.dish_type.system:
                    has_forced_recipes = True
            if len(recipes) > 0 and recipes_have_main_dishtype:
                dish_type_ids = [dish.dish_type_id]
            else:
                # No recipe, return the list of dish types splitted
                dish_type_ids = dish.splitted_dishtype_ids
            dishes.append({"dish_type_ids": dish_type_ids,
                            "main_dish_type_id": dish.dish_type_id,
                            "activated": dish.activated,
                            "id": dish.id,
                            "recipes": recipes,
                            "has_validated_recipes": has_validated_recipes})
        return dishes, has_forced_recipes

class MealSlotLightSerializer(object):
    """
    Hand-made serializer to translate a meal slot into a light object
    * recipe names
    * + infos displayed on popups
    """
    @staticmethod
    def serialize(meal_slot):
        meal_type_name = meal_slot.meal_type.name

        dishes = []
        for dish in sorted(meal_slot.dishes.all(), key=lambda x: x.dish_type_id):
            dish_recipes = []
            for dish_recipe in sorted(dish.dishrecipe_set.all(), key=lambda x: x.order):
                recipe = dish_recipe.recipe
                dish_recipes.append({"id": recipe.id, "name": recipe.name, "ratio": dish_recipe.ratio})
            if len(dish_recipes):
                dishes.append({"id": dish.id, "recipes": dish_recipes,
                               "dish_type_ids": dish.splitted_dishtype_ids})

        return {"id":           meal_slot.id,
                "meal_type":    meal_type_name,
                "dishes":       dishes}

class MealSlotFullSerializer(MealSlotLightSerializer):
    @staticmethod
    def serialize(meal_slot):
        res = MealSlotLightSerializer.serialize(meal_slot)
        res["meal_place"] = meal_slot.meal_place.key
        res["date"] = meal_slot.day.date
        return res

class MealSlotHabitSerializer(object):
    @staticmethod
    def serialize(meal_slot):
        """
        From a mealslot, belonging to a metaplanning, returns the
        content : is it suggested or not, what are the default values in
        both 'suggest' and 'static' mode
        """
        meal_type_dish_types = MealSlotHabitSerializer._get_dish_types(meal_slot)
        dish_type_by_id = dict((dt.id, dt) for dt in meal_type_dish_types)

        dish_conf_by_dt, static_recipe = MealSlotHabitSerializer._get_dish_config(meal_slot, meal_type_dish_types)

        if meal_slot.suggest:
            # Applying aggregations (sub-elements are not configurable, but directly the aggregated dish types)
            MealSlotHabitSerializer.aggregate_dish_types(dish_conf_by_dt)

        assert meal_slot.suggest or not meal_slot.meal_type.force_suggest, "static mealslot that should be suggested"

        return {
            'suggest': {
                'enabled': meal_slot.suggest,
                'dish_types': [dish_conf_by_dt[dt_id] for dt_id in sorted(dish_conf_by_dt.keys())]
            },
            'static': {
                'recipe': MealSlotHabitSerializer._get_static_recipe(meal_slot),
            },
            'can_be_static': not meal_slot.meal_type.force_suggest,
            'speed': meal_slot.speed
        }

    @staticmethod
    def _get_static_recipe(meal_slot):
        custom_dishes = meal_slot.dishes.filter(dish_type__name = DishType.DT_CUSTOM)
        if custom_dishes.count() == 0:
            return None
        assert custom_dishes.count() == 1, "What to do with several custom dishes ?"
        assert custom_dishes[0].dishrecipe_set.count() == 1, "What to do with several custom dishrecipes ?"
        # print("_get_static_recipe", FullRecipeSerializer(custom_dishes[0].dishrecipe_set.get().recipe).data)
        return FullRecipeSerializer(custom_dishes[0].dishrecipe_set.get().recipe).data

    @staticmethod
    def _get_dish_types(meal_slot):
        # Retrieving the list of dish types possible in this meal type (through dish options)
        meal_type_dish_types = []
        for dish_option in meal_slot.meal_type.dish_options.all():
            meal_type_dish_types.append(dish_option.dish_type)
        return meal_type_dish_types

    @staticmethod
    def _get_dish_config(meal_slot, meal_type_dish_types):
        dishes_by_dish_type_id = MealSlotHabitSerializer.index_dishes_by_dish_type(meal_slot)
        dish_conf_by_dt = {} # Configuration of suggested dish_types
        selected_recipes = [] # List of recipes selected in 'static' mode (all forced recipes)

        for dish_type in meal_type_dish_types:
            # Retrieving the list of dishes on this dish_type
            dishes = dishes_by_dish_type_id[dish_type.id]
            recipes = []
            for dish in dishes:
                dishrecipes = list(dish.dishrecipe_set.all())
                assert meal_slot.suggest or dish.dish_type.name != DishType.DT_CUSTOM or len(dishrecipes) == 1, "Non-suggested meal slot with no forced recipe on dish"
                if len(dishrecipes) > 0:
                    assert len(dishrecipes) == 1, "More than 1 dishrecipe forced on 1 dish in metaplanning !"
                    recipes.append(QuickRecipeSerializer(dishrecipes[0].recipe).data)
            if meal_slot.suggest:
                assert len(dishes) <= 1, "More than 1 dishes in for 1 dish_type in suggest mode"
                assert len(recipes) <= 1, "More than 1 recipe forced in suggest mode :/"
                recipe = recipes[0] if len(recipes) else None
                dish = dishes[0] if len(dishes) else None
                dish_conf_by_dt[dish_type.id] = {
                    'name': dish_type.name,
                    'id': dish_type.id,
                    'enabled': dish is not None,
                    'can_be_forced': dish_type.id not in DynamicDishtypes.values(),
                    'forced_recipe': recipe}
            else:
                selected_recipes.extend(recipes)
        return dish_conf_by_dt, selected_recipes

    @staticmethod
    def _get_recipe_options(meal_slot, dish_type_by_id):
        # In "non-suggested" mode, what are the default recipes suggested to the user
        recipe_options = defaultdict(list)
        for recipe in meal_slot.meal_type.static_recipe_options.all():
            # Dish type will be the first dish type of the recipe which is compatible with the meal_type
            recipe_dish_type_ids = set([dt.id for dt in recipe.dish_types.all()])
            recipe_dish_type_ids = recipe_dish_type_ids.intersection(dish_type_by_id.keys())
            assert len(recipe_dish_type_ids) > 0, "Recipe %i is set as default recipe in meal_type %i, but is not compatible" % (recipe.id, meal_slot.meal_type.id)
            recipe_dish_type = dish_type_by_id[list(recipe_dish_type_ids)[0]]
            recipe_options[recipe_dish_type.name].append(QuickRecipeSerializer(recipe).data)
        return recipe_options

    @staticmethod
    def index_dishes_by_dish_type(meal_slot):
        # Indexing dishes by id
        dishes_by_dish_type_id = defaultdict(list)
        for dish in meal_slot.dishes.all():
            dishes_by_dish_type_id[dish.dish_type_id].append(dish)
        return dishes_by_dish_type_id

    @staticmethod
    def aggregate_dish_types(dish_conf_by_dt):
        for master_dish_type, sub_dish_type_ids in detect_aggregations(dish_conf_by_dt.keys(),
                                                                        master_dish_type_object=True).items():
            dish_conf_by_dt[master_dish_type.id] = {
                'name': master_dish_type.name,
                'id': master_dish_type.id,
                'enabled': any(dish_conf_by_dt[sub_dt_id]['enabled'] for sub_dt_id in sub_dish_type_ids),
                'can_be_forced': False, # Aggregated dish types cannot be forced
                'forced_recipe': None
                }
            for sub_dt_id in sub_dish_type_ids:
                del dish_conf_by_dt[sub_dt_id]

class HomeAttendanceSerializer(object):
    @staticmethod
    def serialize(planning, attendances):
        res     = {"days" : [],
                   "places" : dict((place.id, place.key) for place in MealPlace.objects.all()),
                   "meals"  : sorted(list({"id": meal.id, "name": meal.name} for meal in MealType.objects.all()), key=lambda x: x['id']),
                   "eaters" : list({"profile_id" : eater.profile.id,
                                    "name" : eater.profile.nickname,
                                    "is_main": eater.profile.id == planning.user.main_profile_id}
                                   for eater in planning.user.eaters.all())
                  }
        for week_day, day_data in attendances.items():
            day = defaultdict(lambda: defaultdict(dict))
            for meal_type, meal_data in day_data.items():
                for eater, meal_place in meal_data.items():
                    day[meal_type.id][eater.profile.id] = meal_place.key
            res["days"].append(day)
        return res

    @staticmethod
    def deserialize(planning, data):
        mealTypes   = dict((meal.id, meal) for meal in MealType.objects.all())
        mealPlaces  = dict((place.key, place) for place in MealPlace.objects.all())
        eaters      = dict((eater.profile_id, eater) for eater in planning.user.eaters.all())
        attendances = defaultdict(lambda: defaultdict(dict))
        for week_day, day_data in enumerate(data["days"]):
            for meal_id, meal_data in day_data.items():
                for profile_id, place_key in meal_data.items():
                    attendances[week_day][mealTypes[int(meal_id)]][eaters[int(profile_id)]] = mealPlaces[place_key]
        return attendances
