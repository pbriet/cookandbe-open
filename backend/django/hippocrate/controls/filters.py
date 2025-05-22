
from common.array                   import sortBy

from hippocrate.models.filters      import TagRecipeFilter, ExcludeRecipeFilter,\
                                           ExcludeRecipeAllFilter, UstensilFilter,\
                                           ExcludeDataFilter, DishTimeFilter

from optalim.config                 import BUDGET_VALUES

from planning_mgr.controller.planning import get_planning_profiles
from planning_mgr.iterators           import iter_mealslots
from planning_mgr.models            import NotNow

from profile_mgr.models             import RecipeDislike

from recipe_mgr.models              import Ustensil, DishType

from django.utils                   import timezone

import datetime
from optalim.log import logger

class FilterGenerator(object):
    """
    From a list of days, iterate on a list of C++ filters
    """
    def __init__(self, days, profiles=None,
                       enable_diet=True):
        self.days        = days
        self.user        = days[0].user
        self.enable_diet = enable_diet
        if profiles is None:
            profiles  = get_planning_profiles(self.days)
        self.profiles = sorted(profiles, key = lambda x: x.id)

    def __iter__(self):
        """
        Iterate on filters
        The last filters will be the first one to be disabled in case of "too many filters", be
        careful with the order.
        """

        if self.enable_diet:
            yield from self.user.diet_handler.filters()

        # Pathologies/restrictions (critical)
        for profile in self.profiles:
            for restriction in profile.restrictions.all():
                yield TagRecipeFilter(profile, restriction.food_tag)

        # Excluding recipes with ustensils that the user doesn't own
        for ustensil in Ustensil.objects.exclude(pk__in = self.user.ustensils.all()):
            yield UstensilFilter(ustensil)

        # Recipe dislikes
        for dislike in RecipeDislike.objects.select_related('recipe').filter(profile__in=self.profiles):
            yield ExcludeRecipeAllFilter(dislike.recipe)

        # Food dislikes
        for profile in self.profiles:
            # Tastes
            for taste in profile.tastes.all():
                if taste.fondness < 0:
                    yield TagRecipeFilter(profile, taste.food_tag)
                else:
                    raise NotImplementedError

        # Budget
        max_price = BUDGET_VALUES[self.user.budget]["max_filter"]
        yield ExcludeDataFilter("price", -1, max_price)

        # Time
        dish_time_filter = DishTimeFilter()
        for meal in iter_mealslots(self.days):
            if not meal.unlimited_speed:
                speed_infos = meal.cooking_speed_infos['max_minor_recipe_filter']
                for dish in meal.dishes.all():
                    if dish.dish_type.name in (DishType.DT_STARTER, DishType.DT_MAIN_COURSE,
                                               DishType.DT_FULL_COURSE, DishType.DT_SIDE):
                        continue
                    dish_time_filter.add_dish(dish.id, speed_infos['prep_minutes'],
                                         speed_infos['rest_minutes'], speed_infos['cook_minutes'])
        if not dish_time_filter.empty():
            yield dish_time_filter


def iter_disabled_filters(day, dish_recipe):
    """
    On a given dish recipe, in a given day, returns the list of filters that have not been applied correctly
    """
    if dish_recipe.fully_filtered:
        logger.warning("calling get_disabled_filters_human_readable on a fully filtered dishrecipe")
    for filter_ in FilterGenerator([day]):
        if not filter_.py_accept(dish_recipe.dish, dish_recipe.recipe):
            yield filter_

def get_disabled_filters_human_readable(day, dish_recipe):
    """
    Returns disabled filters in text format
    """
    res = []
    for filter_ in iter_disabled_filters(day, dish_recipe):
        res.append(filter_.description())
    return res