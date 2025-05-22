
from planning_mgr.controller.meal   import build_meal
from planning_mgr.models            import MetaPlanning, Day, MealSlot, Dish, MealSlotEater,\
                                           DishType, MealType, DishRecipe
from recipe_mgr.models              import Recipe, Ingredient, RecipeDishType

import copy

def build_mealslot_from_meta(meta_meal_slot, day, meal_place=None, main_profile_id=None):
    if main_profile_id is None:
        main_profile_id = day.user.main_profile_id
    if meal_place is None:
        meal_place = meta_meal_slot.meal_place
     # Cas des repas sautés
    if meal_place.key == "donoteat":
        return None
    new_meal_slot = copy.copy(meta_meal_slot)
    new_meal_slot.day = day
    new_meal_slot.meal_place = meal_place
    new_meal_slot.id = None  # a new id will be auto-generated when saved
    new_meal_slot.save()

    build_meal(new_meal_slot, meta_meal_slot, meal_place.is_external(), main_profile_id=main_profile_id)
    return new_meal_slot

def get_meta_mealslot(meal_type, day, user=None):
    """
    Get the "meta" meal_slot (from metaplanning) for a given day and meal_type
    """
    if user is None:
        user = day.user

    # Same weekday
    meta_day = user.meta_planning.days.get(date=Day.metaplanning_date(day.weekday))
    assert meta_day.weekday == day.weekday

    # Same meal_type
    return meta_day.meal_slots.get(meal_type=meal_type)

def clean_metaplanning(meta_planning):
    """
    Remove all the existing meals and dishes
    """
    for day in meta_planning.days.all():
        for meal_slot in day.meal_slots.all():
            meal_slot.eaters.clear()
            for dish in meal_slot.dishes.all():
                dish.delete()
            meal_slot.delete()
        day.delete()
    clean_internal_user_recipes(meta_planning.user)

def reset_metaplanning(user, speed_value = 2, budget_value = 2):
    """
    For a given user, creates a new meta planning
    It erases the previous one if existing
    """
    if user.meta_planning is None:
        # First meta planning
        meta_planning = MetaPlanning.objects.create(user=user)
        user.meta_planning = meta_planning
        user.save()

    # Get metaplanning
    meta_planning = MetaPlanning.objects.prefetch_related('user__eaters').get(pk=user.meta_planning_id)

    # Remove all the existing meals and dishes
    clean_metaplanning(meta_planning)
    DefaultPlanningBuilder(meta_planning, speed_value, budget_value)()

    # Re-apply handler modifications
    if user.diet is not None:
        diet_handler = user.diet.handler(user.main_profile)
        diet_handler.update_metaplanning(user)

    # Set as modified
    meta_planning.set_modified()
    return meta_planning

class DefaultPlanningBuilder(object):
    def __init__(self, planning, speed_value, budget_value):
        self.planning = planning
        # Global parameter for time available [1-3]
        self.speed_value = speed_value
        # Global parameter for budget [1-3]
        self.budget_value = budget_value
        self.dt_custom_dish_type = None


    def get_dt_ducstom_dish_type(self):
        if self.dt_custom_dish_type is None:
            self.dt_custom_dish_type = DishType.get_dt(DishType.DT_CUSTOM)
        return self.dt_custom_dish_type


    def __call__(self):
        meal_types = MealType.objects.order_by('id').prefetch_related('dish_options__dish_type')
        days_to_create = []
        for week_day in range(7):
            days_to_create.append(Day(user=self.planning.user,
                                     date=Day.metaplanning_date(week_day),
                                     planning=self.planning))
        days_to_create = Day.objects.bulk_create(days_to_create)
        days = []
        # This code is specific for the tests has bulk_create doesn't return ids in Sqlite
        for day in days_to_create:
            if day.id is None:
                day = Day.objects.get(date=day.date, user_id=day.user_id)
            days.append(day)
        # Now we have days with ids in PostgreSql and Sqlite
        self.planning.days.add(*days)

        for day in days:
            for meal_type in meal_types:
                meal_slot = self.create_meal_slot(day, meal_type)

                # By default, all profiles are eating to every meal
                ms_eaters = []
                for eater in self.planning.user.eaters.all():
                    if eater.regular:
                        ms_eaters.append(MealSlotEater(meal_slot=meal_slot, eater=eater))
                MealSlotEater.objects.bulk_create(ms_eaters)

    def create_meal_slot(self, day, meal_type):
        """
        Shortcut to create quickly a meal slot
        """
        meal_slot = MealSlot.objects.create(day         = day,
                                            meal_type   = meal_type,
                                            meal_place_id = meal_type.default_place_id,
                                            time        = meal_type.time,
                                            speed       = self.speed_value,
                                            suggest     = meal_type.default_suggest)
        self.reset_mealslot(meal_slot, user = day.user, clean=False)
        return meal_slot

    def _get_custom_recipe(self, meal_slot, user):
        custom_dishtype = DishType.get_dt(DishType.DT_CUSTOM)
        custom_dish = Dish.objects.create(meal_slot = meal_slot, order = 0, dish_type = custom_dishtype, optional = False)
        query = Recipe.objects.filter(internal = True, author = user, dishrecipe__dish__meal_slot__meal_type = meal_slot.meal_type)
        query = query.filter(dishrecipe__dish__meal_slot__day__planning = user.meta_planning).distinct()
        if query.count() == 0:
            custom_recipe = self._create_custom_recipe(meal_slot, user)
        else:
            assert query.count() == 1, "Too many custom recipes for mealtype '%s' (%i)" % (meal_slot.meal_type.name, query.count())
            custom_recipe = query[0]
        DishRecipe.objects.create(dish = custom_dish, recipe = custom_recipe, ratio = 1.0, order = 1, user = user, validated = True)
        return custom_recipe

    def _create_custom_recipe(self, meal_slot, user):
        custom_recipe_name = meal_slot.meal_type.name
        if user.main_profile is not None:
            custom_recipe_name += " de %s" % user.main_profile.nickname
        custom_recipe = Recipe.objects.create(
            name = custom_recipe_name,
            author = user,
            status = 1,
            prep_minutes = 0,
            cook_minutes = 0,
            rest_minutes = 0,
            price = 1,
            difficulty = 1,
            nb_people = 1,
            internal = 1,
        )
        RecipeDishType.objects.create(recipe = custom_recipe, dish_type = self.get_dt_ducstom_dish_type())
        ingredients_to_create = []
        for dish_option in meal_slot.meal_type.dish_options.filter(default_recipe__isnull = False, min_budget_check__lte = 2, min_speed_check__lte = 2):
            for ingredient in dish_option.default_recipe.ingredients.all():
                ingredients_to_create.append(Ingredient(
                    recipe = custom_recipe, food = ingredient.food, grams = ingredient.grams,
                    default_conversion = ingredient.default_conversion, raw_state = ingredient.raw_state,
                    cooking_method = ingredient.cooking_method, previously_cooked = ingredient.previously_cooked
                ))
        Ingredient.objects.bulk_create(ingredients_to_create)
        return custom_recipe

    def should_dish_option_be_checked(self, dish_option):
        """
        Returns true if the dish_option should be checked by default, depending on time and budget values
        """
        if dish_option.min_speed_check is None or dish_option.min_budget_check is None:
            return False
        if self.speed_value >= dish_option.min_speed_check and self.budget_value >= dish_option.min_budget_check:
            return True
        return False

    def reset_mealslot(self, meal_slot, user = None, clean=True):
        """
        Removes and rebuilds all the dishes with default options
        """
        if clean:
            meal_slot.dishes.all().delete()
        if user is None:
            user = meal_slot.day.user
        meal_type = meal_slot.meal_type
        custom_recipe = None
        if meal_slot.meal_type.force_suggest is False:
            custom_recipe = self._get_custom_recipe(meal_slot, user)
        dishes_to_create = []
        for i, dish_option in enumerate(sorted(meal_type.dish_options.all(), key=lambda x: x.id)):
            if self.should_dish_option_be_checked(dish_option):
                dishes_to_create.append(Dish(meal_slot = meal_slot, order = i,
                                           dish_type = dish_option.dish_type,
                                           optional = dish_option.default_optional,
                                           activated = dish_option.dish_type.is_activated_by_default()))
        Dish.objects.bulk_create(dishes_to_create)


def check_can_auto_update_from_meta(user, day):
    """
    Returns true if days can automatically be rebuilt from a given date (7 days starting this date)
    * If there is no validated day after
    * If current day is not skipped or in a shopping list
    """
    if not day.requires_update(user=user):
        # Metaplanning has not changed
        return False
    if day.shopping_list_id is not None or day.skipped is not None:
        # Has a shopping_list : this day is locked, can't update it from meta
        # Is skipped : don't touch it, it will remove its status  (TODO: allow the algorithm to reset locked days)
        return False

    # No shopping list - not skipped
    # Checking if next days are validated
    next_days = user.days.filter(date__gt=day.date)
    if not all(d.skipped is None or d.skipped for d in next_days):
        # There ares days already visited : can't update automatically
        return False
    return True # Bingo!

def clean_internal_user_recipes(user):
    """
    Remove all user internal recipes which are no longer bound to any planning through a dishrecipe
    """
    recipes = Recipe.objects.filter(author = user, internal = True, dishrecipe__isnull = True)
    recipes.delete()

