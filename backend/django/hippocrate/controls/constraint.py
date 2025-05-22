from django.db.models               import Max
from django.utils                   import timezone
from eater_mgr.ratios               import RatiosCalculator
from hippocrate_cpp.core                import DishIndex, IdVector
from hippocrate.models.constraints  import UnicityConstraint, RedundancyConstraint
from hippocrate.models.constraints  import BudgetConstraint, UnicityFoodTagConstraint, ProteinsConstraint
from hippocrate.models.constraints  import RecipesPenaltiesConstraint
from hippocrate.models.database     import Diet
from planning_mgr.models            import Day
from optalim.config                 import BUDGET_VALUES, MEAT_LEVELS, FISH_LEVELS
from optalim.settings               import TESTING
from recipe_mgr.models              import DishType, FoodTag, Recipe

import datetime

class ConstraintGenerator(object):
    """
    From a problem, returns a list of constraints
    """
    def __init__(self, problem):
        self.problem = problem
        self.user = self.problem.user
        self.profiles = self.problem.profiles
        self.planning = self.problem.planning
        self.enable_diet = self.problem.enable_diet

        self.main_profile_ratio = RatiosCalculator(self.user).get_main_profile_ratio()

        # Dish_type that we want unique over the week  (1 recipe per dish_type)
        unique_dish_type_names = [DishType.DT_STARTER, DishType.DT_MAIN_COURSE, DishType.DT_FULL_COURSE,
                                  DishType.DT_SIDE]

        # Unique on a day only
        day_unique_dish_type_names = [DishType.DT_SNACK_SWEET, DishType.DT_SNACK_SALTED, DishType.DT_DESSERT, DishType.DT_FRUIT]

        # Dish type for which we want to encourage redundancy
        # (non-fully monotonous)
        redundant_dish_type_names = [DishType.DT_SNACK_SWEET, DishType.DT_SNACK_SALTED,
                                     DishType.DT_BEVERAGE, DishType.DT_SNACK,DishType.DT_CHEESE,
                                     DishType.DT_BEVERAGE_COLD, DishType.DT_DESSERT, DishType.DT_FRUIT]

        dish_type_id_by_name = dict((dt.name, dt.id) for dt in DishType.objects.filter(monotonous=False))

        self.unique_dish_type_ids = self._load_dish_type_ids(dish_type_id_by_name, unique_dish_type_names)
        self.day_unique_dish_type_ids = self._load_dish_type_ids(dish_type_id_by_name, day_unique_dish_type_names)
        self.redundant_dish_type_ids = self._load_dish_type_ids(dish_type_id_by_name, redundant_dish_type_names)


    def __iter__(self):
        yield from self.diet_constraints()
        yield from self.recipe_constraints()
        yield from self.other_constraints()

    def diet_constraints(self):
        """
        Initialize all the constraints related to the diets
        followed by any profile involved
        """
        # NOTE: for the moment, only the main user profile is allowed to follow a diet.
        if self.user.main_profile is not None and self.enable_diet:
            diet_handler = self.user.diet_handler
            yield from diet_handler.build_nutrient_constraints(self.planning)

    def _load_dish_type_ids(self, dish_type_id_by_name, dish_type_names):
        """
        Return dishtype ids from dish_type names
        """
        res = []
        for name in dish_type_names:
            dish_type_id = dish_type_id_by_name.get(name, None)
            if dish_type_id is None:
                assert TESTING, "No such dishtype : %s (or monotonous ?)" % name
                continue
            res.append(dish_type_id)
        return res


    def other_constraints(self):
        """
        Initialize all the default constraints :
        * On some dish types, we want to ensure that there isn't twice the same recipe (like main dish)
        * On some others, we want to ensure that it is quite redundant (like cheese)
        """
        if len(self.unique_dish_type_ids):
            yield UnicityConstraint(1000, self.unique_dish_type_ids, self.day_unique_dish_type_ids)

        if len(self.profiles) == 1:
            # Singles: at least 3 portions of each recipe
            nb_min_portions_per_recipe = 3
        else:
            # Families: at least 5 portions of each recipe
            nb_min_portions_per_recipe = 5

        if len(self.redundant_dish_type_ids):
            yield RedundancyConstraint(5, self.redundant_dish_type_ids, nb_min_portions_per_recipe)

        # Food Tag Constraints
        unique_food_tags = FoodTag.objects.filter(name__in=["Pâtes", "Riz", "Couscous", "Poisson"])
        unique_food_tag_ids  = IdVector()
        for ft in unique_food_tags:
            unique_food_tag_ids.append(ft.id)
        yield UnicityFoodTagConstraint(200, unique_food_tag_ids)

        # Max budget
        max_avg_price = BUDGET_VALUES[self.user.budget]["max_avg"]
        if max_avg_price is not None:
            yield BudgetConstraint(max_avg_price, 10)

        yield from self.proteins_constraints()


    def recipe_constraints(self):
        """
        Get constraints that penalize some recipes for a given user
        """
        recipe_penalities = {}

        # Penality on recipes recently suggested
        planning_start_date = self.planning.start_date()
        recent_dates_min = planning_start_date - datetime.timedelta(days=30)
        recent_days = Day.objects.only('id').filter(date__gte=recent_dates_min, skipped=False)
        recent_recipes = Recipe.objects.only('id').filter(dishrecipe__dish__meal_slot__day__date__gte=recent_dates_min,
                                                          dishrecipe__dish__meal_slot__day__date__lt=planning_start_date,
                                                          dishrecipe__dish__dish_type_id__in=self.unique_dish_type_ids,
                                                          dishrecipe__dish__meal_slot__day__user_id=self.planning.user_id)
        recent_recipes = recent_recipes.extra(
                            select={'day_date': '"planning_mgr_day"."date"'})

        ctr = RecipesPenaltiesConstraint()
        for recipe in recent_recipes:
            ctr.add_penalty(recipe.id, 400 / max(1, (planning_start_date - recipe.day_date).days)**0.5)

        # Not nows : on a 30 days period, retrieve recipes that were asked to be "not now"
        # The sooner it's been done, the stronger the penalty is
        not_nows = self.user.recent_not_nows
        for not_now in not_nows:
            if (timezone.now() - not_now.created_at).seconds < 30:
                # Huge penalty for very recent not nows
                penalty = 10000
            else:
                penalty = max(0, 400 - (0.66*(timezone.now() - not_now.created_at).days) ** 2)
            ctr.add_penalty(not_now.recipe_id, penalty)

        for personal_recipe in self.problem.own_recipes:
            if not personal_recipe.is_custom():
                # Encouraging personal recipes
                ctr.add_penalty(personal_recipe.id, -20)
        for cookbook_recipe in self.user.cookbook_recipes.all():
            # Encouraging favorite recipes
            ctr.add_penalty(cookbook_recipe.recipe_id, -20)

        yield ctr


    def proteins_constraints(self):
        meat_params = MEAT_LEVELS[self.user.meat_level]
        fish_params = FISH_LEVELS[self.user.fish_level]
        proteins_limits = []
        if meat_params is not None:
            proteins_limits.append(("meat",) + meat_params)
        if fish_params is not None:
            proteins_limits.append(("fish",) + fish_params)

        for proteins_key, min_value, max_value, tolerance in proteins_limits:
            min_value *= self.main_profile_ratio
            max_value *= self.main_profile_ratio
            yield ProteinsConstraint(proteins_key, min_value, max_value,
                                    daily_tolerance_min=tolerance,
                                    daily_tolerance_max=tolerance,
                                    cost_per_percent_out=50)

