"""
This file contains the main class Problem, which is used by Hippocrate to handle a week generation.
"""
from collections import defaultdict

from common.boost import to_dict
from django.utils import timezone
from optalim.settings import TESTING, ENABLE_MONGO_TESTING, DEBUG

from eater_mgr.ratios import RatiosCalculator

from hippocrate_cpp.core import DishIndex, Solution, build_solution, ExcludeRecipeFilter
from hippocrate_cpp.core import Problem as ProblemC
from hippocrate.models.recipestorage import MainRecipeStorage
from hippocrate.models.recipe import RecipeDataBuilder
from hippocrate.models.database import DishRecipe, DishTypeAggregation, DishTypeUnion
from hippocrate.models.constraints import TimeConstraint, MaxModifsConstraint, MealBalanceConstraint
from hippocrate.models.constraints import NutrientConstraint, NutrientWeekRule, ShoppingConstraint
from hippocrate.controls.constraint import ConstraintGenerator
from hippocrate.controls.filters import FilterGenerator
from hippocrate.controls.dish_indexing import cpp_dish_from_dish

from memory.controls import MemoryManager

from nutrient.models import Nutrient

from planning_mgr.controller.planning import get_planning_profiles
from planning_mgr.iterators import iter_mealslots, iter_dishes

from profile_mgr.models import Profile

from recipe_mgr.models import Recipe, DishType
from recipe_mgr.seasons import SeasonManager

import sys
import copy
import time

# Logs
from optalim.log import logger

EATER_RATIO_THRESHOLD = 3.0


def log_time_decorator(chrono_name):
    """
    Decorator to store into "self.chronos[name]" CPU and real time
    """

    def dec(fcn):
        def new_fcn(self, *args, **kargs):
            if TESTING and not ENABLE_MONGO_TESTING:
                return fcn(self, *args, **kargs)  # No logs in tests
            start_time = time.time(), time.perf_counter()
            res = fcn(self, *args, **kargs)
            # Storing how much time the initialization took
            self.add_time_log(chrono_name, *start_time)
            return res

        return new_fcn

    return dec


class Problem(ProblemC):
    """
    Contains all elements required to describe and solve a planning generation problem.
    """

    DEFAULT_MAXIMUM_SOLVING_MILLISECONDS = 12500
    user = property(lambda slf: slf.days[0].user)
    planning = property(lambda slf: slf.days[0].planning.planning)

    @log_time_decorator("init")
    def __init__(
        self,
        days,
        forced_constraints=None,
        enable_diet=True,
        init_recipe_indexes=True,
        dish_ids=None,
        minimize_change=None,
        start_from_existing_solution=False,
        current_day=None,
        make_validated_mutable=False,
    ):
        """
        Create a problem related to given list of days.
        @param dish_ids: if set, only these dish ids can change. The other can only vary on quantities.
        @param minimize_change: valid only with start_from_existing_solution=True. 3 modes :
                                - None: Won't try to limit dish modifications
                                - 'weak': Will try to minimize the number of modifications, but with no priority over diet
                                - 'strong': Will ~equally consider modification cost and diet cost
        """
        assert len(days), "No days provided"

        self.days = sorted(days, key=lambda x: x.date)
        self.minimize_change = minimize_change
        assert minimize_change in (None, "weak", "strong"), "Invalid value for minimize_change"
        self.make_validated_mutable = make_validated_mutable
        self.dish_ids = dish_ids
        self.dishes_by_ids = {}
        self.start_from_existing_solution = start_from_existing_solution
        self.py_constraints = []  # Python copy of all constraints (needed by the garbage collector to prevent premature free)
        self.py_filters = set()  # Python copy of all filters (needed by the garbage collector to prevent premature free)
        self.current_day = current_day

        self.static_dishes = []  # List of dishes that are defined by the user <> shouldn't be changed by the algorithm

        # If True, add the constraints related to diet
        self.enable_diet = enable_diet

        # Initialize food ratios
        self.ratios_calculator = RatiosCalculator(self.user)

        # Initializing ratios from meal structure
        self.initial_ratios = self.ratios_calculator.get_initial_ratios(self.days)
        self.dish_ratios = copy.copy(self.initial_ratios)
        if start_from_existing_solution:
            # Retrieving existing ratios from BDD
            self.dish_ratios.update(self.ratios_calculator.get_ratios_from_bdd(self.days))

        self.profiles = get_planning_profiles(self.days)
        # Parse the database hierarchy : Planning > MealSlot > Dish
        self.dish_index = self.init_dish_index()
        # Add personal recipes in recipe index
        self.build_recipe_list()
        # C++ initialization
        ProblemC.__init__(self, self.dish_index, self.DEFAULT_MAXIMUM_SOLVING_MILLISECONDS)

        self.set_main_profile_id(self.user.main_profile_id)
        for profile_id, ratio in self.ratios_calculator.profile_ratios.items():
            self.set_profile_ratio(profile_id, ratio)

        self.init_filters()

        # Build the initial solution, the one we're starting from
        self.__initial_solution = self.build_current_solution()
        self.set_initial_solution(self.__initial_solution)
        self.stick_to_initial_solution(start_from_existing_solution)
        if not start_from_existing_solution:
            self.init_cookbook_recipes()

        # Set the mutable ids (initialize some filters if partial)
        if dish_ids:
            self.init_partial_regenerate(dish_ids)
        else:
            self.dish_index.set_fully_mutable()
            for dish_id in self.static_dishes:
                self.dish_index.set_not_mutable(dish_id)

        if forced_constraints:
            # Dedicated to testing
            self.init_forced_constraints(forced_constraints)
        else:
            # Add filters and constraints profile-related
            self.init_constraints()

        # Initialize the optimization buffers on the initial solution
        self.__initial_solution.init_constraint_buffers()

        ### NB: need to be done AFTER all filters added
        # Calculates the domains for each dish
        # Initialize DishIndex internals
        self.init_dishdomains(self._recipes, init_recipe_indexes)

    def build_recipe_list(self):
        """
        Extends the global recipe index with the personal recipes of the user
        """
        self._recipes = list(MainRecipeStorage.published_recipes(filter_season=True))
        own_recipes = (
            Recipe.objects.filter(author=self.user, status__gte=Recipe.STATUS_VALIDATED, status__lte=Recipe.STATUS_REVIEWING)
            .only("id")
            .prefetch_related("dish_types")
        )
        self.own_recipes = [recipe for recipe in own_recipes if SeasonManager.is_seasonal(recipe.id, update_if_missing=True)]
        own_recipes_data = RecipeDataBuilder().get_or_build_many([r.id for r in self.own_recipes])
        for rdata in own_recipes_data:
            self._recipes.append(rdata)

    def add_constraint(self, c):
        """
        Add a constraint to the problem.
        Note that the constraint is stored in both the C++ object and the Python object,
        so that the garbage collector doesn't clean unreferenced pointers.
        """
        # Not the best place, but handlers should be able to control the final constraints
        if self.user.main_profile is not None and self.enable_diet:
            c = self.user.diet_handler.validate_constraint(c)
        if c is None:
            return
        self.py_constraints.append(c)
        ProblemC.add_constraint(self, c)

    def get_constraint(self, id_):
        for ctr in self.py_constraints:
            if ctr.id == id_:
                return ctr
        return None

    @log_time_decorator("solve")
    def solve_darwin(self, *args, **kargs):
        return super().solve_darwin(*args, **kargs)

    def build_current_solution(self):
        """
        Converts the current days to a solution to this problem
        """
        dish_id_to_recipe_data = {}
        dish_id_to_ratio = {}
        for meal_slot in iter_mealslots(self.days):
            if meal_slot.meal_type.name == "donoteat":
                continue
            for dish in meal_slot.dishes.all():
                self.dishes_by_ids[dish.id] = dish
                dish_id_to_ratio[dish.id] = self.dish_ratios[dish.id]
                if self.dish_ratios[dish.id] <= 0.2:
                    raise Exception("Invalid default dish ratio : %s for dish %s" % (self.dish_ratios[dish.id], dish.id))
                recipe_datas = []
                for dish_recipe in sorted(dish.dishrecipe_set.all(), key=lambda x: x.order):
                    if dish_recipe.ratio <= 0:
                        raise Exception("Invalid stored dishrecipe ratio : %s for dish %s" % (dish_recipe.ratio, dish.id))
                    recipe_datas.append(MainRecipeStorage.get(dish_recipe.recipe_id))
                    dish_id_to_ratio[dish.id] = dish_recipe.ratio
                dish_id_to_recipe_data[dish.id] = recipe_datas

        return build_solution(self, dish_id_to_recipe_data, dish_id_to_ratio)

    @log_time_decorator("clean_solution")
    def clean_previous_solution(self):
        """
        Removes the recipes stored in the database for this problem
        """
        # Remove the existing DishRecipes
        DishRecipe.objects.filter(dish__id__in=self.dish_index.mutable_dish_ids).delete()

    @log_time_decorator("save_solution")
    def save_solution(self, solution):
        dish_id_to_dishrecipes = to_dict(solution.get_dish_recipes())
        if DEBUG:
            self._assert_not_mutables_validity(dish_id_to_dishrecipes)
        dish_recipe_objects = []
        for dish_id, cpp_dishrecipes in dish_id_to_dishrecipes.items():
            if dish_id in self.dish_index.mutable_dish_ids:
                self._save_solution_dish(dish_recipe_objects, dish_id, cpp_dishrecipes)

        # Create objects in the DB (one query)
        DishRecipe.objects.bulk_create(dish_recipe_objects)

    def init_cookbook_recipes(self):
        """
        Put in the problem the list of cookbook recipes and personal recipes
        """
        for cookbook_recipe in self.user.cookbook_recipes.all():
            self.add_favorite_recipe(cookbook_recipe.recipe_id)
        for personal_recipe in self.own_recipes:
            if not personal_recipe.is_custom():
                self.add_favorite_recipe(personal_recipe.id)

    def _save_solution_dish(self, dish_recipe_objects, dish_id, cpp_dishrecipes):
        """
        Save DishRecipes for one given dish
        """
        for i, cpp_dishrecipe in enumerate(cpp_dishrecipes):
            assert cpp_dishrecipe.dish_id == dish_id
            dish = self.dishes_by_ids[dish_id]
            if cpp_dishrecipe.ratio <= 0.2:
                raise Exception("Invalid dishrecipe ratio : %s for dish %s" % (cpp_dishrecipe.ratio, dish_id))

            dish_recipe_objects.append(
                DishRecipe(
                    dish_id=dish_id,
                    recipe_id=cpp_dishrecipe.recipe.recipe_id,
                    ratio=cpp_dishrecipe.ratio,
                    order=cpp_dishrecipe.order,
                    in_shopping_list=dish.activated,
                    fully_filtered=cpp_dishrecipe.fully_filtered,
                )
            )

    def _assert_not_mutables_validity(self, dish_id_to_dishrecipes):
        """
        Ensure that the dishrecipes returned by the algorithm are the same as the one in the database
        (DEBUG only)
        """
        # Dish_id : set([(recipe_id, ratio)])
        existing = defaultdict(set)
        for dish in iter_dishes(self.days):
            for dishrecipe in dish.dishrecipe_set.all():
                existing[dish.id].add((dishrecipe.recipe_id, dishrecipe.ratio))

        # From solution
        for dish_id, cpp_dishrecipes in dish_id_to_dishrecipes.items():
            if dish_id in self.dish_index.mutable_dish_ids:
                continue  # This is a mutable dish, it is meant to change
            values = set()
            for cpp_dishrecipe in cpp_dishrecipes:
                values.add((cpp_dishrecipe.recipe.recipe_id, cpp_dishrecipe.ratio))
            assert values == existing[dish_id], "Different dish values on non mutable dish %i : %s => %s" % (dish_id, existing[dish_id], values)

    def init_dish_index_meal_slot(self, dish_index, day, meal_slot, static_recipes):
        nb_dishes = 0
        eaters = list(meal_slot.eaters.all())
        assert len(eaters) > 0, "Active mealslot with no eater (%s, %s)" % (meal_slot.meal_name, meal_slot.meal_place.key)
        # For each dish, creates a C++ dish and storing it in the DishIndex
        for dish in meal_slot.dishes.all():
            # Création du dish
            initial_ratio = self.initial_ratios[dish.id]
            cpp_dish = cpp_dish_from_dish(dish, meal_slot=meal_slot, initial_ratio=initial_ratio)
            # Sécurité
            assert initial_ratio is not None
            if initial_ratio > EATER_RATIO_THRESHOLD * len(eaters):
                logger.critical(
                    "SUSPECT GLOBAL DISH RATIO (ratio %f, %i eaters, on day %i of user %i)" % (initial_ratio, len(eaters), day.id, day.user.id)
                )

            existing_dish_ratio = self.dish_ratios[dish.id]
            assert not dish.dish_type.has_static_ratio() or (initial_ratio == 1 and existing_dish_ratio == 1)
            # Pour les plats existants (forcés ou déjà calculés), utilisation du ratio global
            for existing_recipe in dish.dishrecipe_set.all():
                if existing_dish_ratio != existing_recipe.ratio:
                    if existing_dish_ratio <= 0.2:
                        raise Exception("Setting init_dish_index_meal_slot ratio : %s" % existing_dish_ratio)
                    existing_recipe.ratio = existing_dish_ratio
                    existing_recipe.save()
            # Calcul du ratio des recettes forcées
            dish_index.add_dish(cpp_dish)
            dish_static_recipes = [r for r in static_recipes if r.dish == dish]
            if len(dish_static_recipes) > 0:
                self.static_dishes.append(dish.id)
            nb_dishes += 1
        return nb_dishes

    @log_time_decorator("dish_index")
    def init_dish_index(self):
        """
        Initialize the C++ object containing dishes.
        Nearly a mirror of Dish / DishTypes
        """
        day_ids = [day.id for day in self.days]
        dish_recipes = DishRecipe.objects.filter(dish__meal_slot__day_id__in=day_ids).select_related("dish__meal_slot__day")

        def is_static(dr):
            # Returns true if this dish_recipe is static
            if dr.user_id is not None or (dr.validated and not self.make_validated_mutable):
                return True  # Cannot mutate a forced or validated recipe
            day = dr.dish.meal_slot.day
            if self.current_day is None or day.id == self.current_day.id:
                return False  # Current day is mutable
            return day.is_validated()  # Other days are mutables if they're not validated

        static_recipes = [sr for sr in dish_recipes if is_static(sr)]

        d = DishIndex()
        nb_dishes = 0
        for day in self.days:
            for meal_slot in day.meal_slots.all():
                if meal_slot.meal_type.name == "donoteat":
                    continue
                nb_dishes += self.init_dish_index_meal_slot(d, day, meal_slot, static_recipes)

        assert nb_dishes > 0, "Empty dish index"

        for dish in iter_dishes(self.days):
            if dish.dish_type.monotonous:
                d.add_monotonous_dishype(dish.dish_type_id)

        # Saying to the C++ what are the aggregations and unions
        for aggregation in DishTypeAggregation.objects.order_by("id").all():
            d.add_dishtype_aggregation(aggregation.master_dish_type_id, aggregation.sub_dish_type_id)
        for union in DishTypeUnion.objects.all():
            d.add_dishtype_union(union.master_dish_type_id, union.sub_dish_type_id)
        return d

    def init_partial_regenerate(self, dish_ids):
        """
        If this is an update, we retrieve the current solution
        and define it as the initial (+ keeping a python pointer for memory issues)
        """
        # We remove the current dish recipes from the domains, so that the result is different
        dish_id_to_recipes = to_dict(self.__initial_solution.get_recipes())
        for dish_id in dish_ids:
            self.dish_index.add_mutable_dish(dish_id)
            for recipe in dish_id_to_recipes[dish_id]:
                self.add_filter(ExcludeRecipeFilter(dish_id, recipe.recipe_id))

    def add_filter(self, f):
        """
        Add a filter to the problem.
        Note that the filter is stored in both the C++ object and the Python object,
        so that the garbage collector doesn't clean unreferenced pointers.
        """
        self.py_filters.add(f)
        ProblemC.add_filter(self, f)

    def init_forced_constraints(self, forced_constraints):
        for constraint in forced_constraints:
            self.add_constraint(constraint)

    def add_additional_constraints(self):
        day_id = -1  # Meaning no day_id in C++...
        if self.current_day is not None:
            day_id = self.current_day.id
        if self.minimize_change == "strong":
            # Allowing up to 2 modifications without penalties. Cost of 500 per additional modification
            self.add_constraint(MaxModifsConstraint(self.__initial_solution, 2, 100, day_id))
        elif self.minimize_change == "weak":
            # Any modification has a cost, but low. Prioritize diet improvements, but try to minimize
            self.add_constraint(MaxModifsConstraint(self.__initial_solution, 0, 30, day_id))

    def init_constraints(self):
        """
        Initialize all constraints and filters
        * Nutrient constraints related to Diet
        * Time constraints on each meal
        * Redundancy, Unicity, ...
        """
        # NOTE: for the moment, only the main user profile is allowed to follow a diet.
        # Adding Diet constraints.
        for constraint in ConstraintGenerator(self):
            self.add_constraint(constraint)

        timeConstraint = TimeConstraint(0.05)  # Cost by exceeding square minute
        for meal in iter_mealslots(self.days):
            if not meal.unlimited_speed:
                speed_infos = meal.cooking_speed_infos["max_per_meal"]
                timeConstraint.add_meal_time_limit(meal.id, speed_infos["prep_minutes"], speed_infos["cook_minutes"], speed_infos["rest_minutes"])
        if not timeConstraint.empty():
            self.add_constraint(timeConstraint)

        # Meal balance between dinner and lunch
        # Dinner should between 70% and 100% of lunch
        meal_balance = MealBalanceConstraint(Nutrient.NUT_CALORIES, 0.6, 1, 3)
        for day in self.days:
            lunch_id, dinner_id = None, None
            for meal in day.meal_slots.all():
                if not meal.suggest:
                    continue
                if meal.meal_type.key == "lunch":
                    lunch_id = meal.id
                elif meal.meal_type.key == "dinner":
                    dinner_id = meal.id
            if lunch_id is not None and dinner_id is not None:
                meal_balance.add_lunch_dinner_pair(lunch_id, dinner_id)
        self.add_constraint(meal_balance)
        # Disabling nb_list_item penalty
        # self.add_constraint(ShoppingConstraint(MemoryManager.food_index, 50, 1, 20))
        self.add_constraint(ShoppingConstraint(MemoryManager.food_index, 0, 0, 10))
        self.add_additional_constraints()

    @log_time_decorator("init_filters")
    def init_filters(self):
        """
        Add filters that excludes some recipes in the domains
        """
        for filter_ in FilterGenerator(self.days, self.profiles, enable_diet=self.enable_diet):
            self.add_filter(filter_)

    def get_results(self):
        """
        Helper to retrieve the list of DishRecipes found for this problem
        """
        return DishRecipe.objects.filter(dish__meal_slot__day_id__in=[d.id for d in self.days])

    def add_time_log(self, chrono_name, start_real_time, start_cpu_time):
        """
        Stores a time information (logging)
        """
        if not hasattr(self, "chronos"):
            self.chronos = {}
        self.chronos[chrono_name] = {"real": time.time() - start_real_time, "cpu": time.perf_counter() - start_cpu_time}

    def get_constraint_intervals(self, solution):
        """
        Returns constraint details for each day.
        """
        score = self.eval(solution, False)
        daily_res = {}
        week_res = {}
        for nutrient_constraint in self.py_constraints:
            if not isinstance(nutrient_constraint, NutrientConstraint):
                continue
            daily_values = []
            for rule in nutrient_constraint.rules:
                if type(rule) is NutrientWeekRule:
                    week_value = rule.get_value(solution)
                    week_res[nutrient_constraint.description()] = [
                        nutrient_constraint.min_value,
                        nutrient_constraint.max_value,
                        week_value / len(self.days),
                    ]
                else:
                    day_nutrient_value = rule.get_value(solution)
                    # description = "%s %s" % (round(day_nutrient_value, 2), nutrient_constraint.nutrient.unit)
                    daily_values.append(day_nutrient_value)
            if len(daily_values) == 0:
                assert not nutrient_constraint.enable_day_constraints()
                continue
            min_day_value, max_day_value = -1, -1
            if nutrient_constraint.daily_tolerance_min >= 0:
                min_day_value = nutrient_constraint.min_value * (1 - float(nutrient_constraint.daily_tolerance_min))
            if nutrient_constraint.daily_tolerance_max >= 0:
                max_day_value = nutrient_constraint.max_value * (1 + float(nutrient_constraint.daily_tolerance_max))
            daily_res[nutrient_constraint.description()] = [min_day_value, max_day_value, daily_values]
        # Return days ordered
        return daily_res, week_res
