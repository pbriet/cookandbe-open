
from common.math                import round_to_closest

from collections                import defaultdict

from hippocrate.models.recipe   import RecipeDataBuilder

from nutrient.models            import Nutrient

from planning_mgr.iterators     import iter_dishrecipes, iter_mealslots

from profile_mgr.models         import Profile

from recipe_mgr.models          import DishType

from optalim.log import logger

# Will make sure that default structure ratios are between 0.5 and 2
ENABLE_DAY_RATIO_SECURITY = True

class InvalidEaterException(Exception):
    def __init__(self, day, profile_id):
        self.day = day
        self.profile_id = profile_id

    def __str__(self):
        return "Profile %i eating during day %s isn't registered in meal slots" % (self.profile_id, self.day.date)

def get_theoretical_dish_calories(dish):
    """
    On a given dish, returns a pair of values
    (Number of 'static' calories - for which the ratio cannot be modified,
     Number of 'dynamic' calories - that have a variable ratio)
    """
    if dish.dish_type.standard_calories is not None:
        return 0, dish.dish_type.standard_calories
    # No standard calories defined for this type, dishrecipes are forced  (custom or external)
    recipe_ids = [dr.recipe_id for dr in dish.dishrecipe_set.all()]
    if not dish.dish_type.has_static_ratio():
        logger.critical("no standard calories for dish_type %s" % dish.dish_type.name)
    if len(recipe_ids) == 0:
        logger.critical("dish with no standard calories and no recipes (id=%i, type=%s)" % (dish.id, dish.dish_type.name))
    recipe_data = RecipeDataBuilder().get_or_build_many(recipe_ids)
    return sum(rdata.get_data_from_key(Nutrient.NUT_CALORIES, 1) for rdata in recipe_data), 0



class RatiosCalculator(object):

    # Profiles property : list of user profiles (all)
    def get_profiles(self):
        if self._profiles is None:
            self._retrieve_profiles()
        return self._profiles
    profiles = property(get_profiles)

    # Profile ratios : profile_id -> ratio  (not related to a dish. Global profiles ratios)
    def get_profile_ratios(self):
        if self._profile_ratios is None:
            self._calc_profile_ratios()
        return self._profile_ratios
    profile_ratios = property(get_profile_ratios)

    # Profile calories : profile_id -> required calories input
    def get_profile_calories(self):
        if self._profile_calories is None:
            self._calc_profile_calories()
        return self._profile_calories
    profile_calories = property(get_profile_calories)

    def __init__(self, user):
        self.user = user
        self._profiles = None
        self._profile_ratios = None
        self._profile_calories = None # Theorical calories

    def _retrieve_profiles(self):
        """
        Retrieve profiles from BDD
        """
        self._profiles = list(Profile.objects.filter(creator=self.user))

    def _calc_profile_calories(self):
        """
        For each profile, calculated its theorical caloric need
        """
        profiles = self.profiles
        assert len(profiles) > 0
        user = self.user

        self._profile_calories = {}
        for profile in profiles:
            self._profile_calories[profile.id] = profile.caloric_need()
            if user.main_profile_id == profile.id and user.diet_id:
                # Specific modifications of ratio according to the diet
                self._profile_calories[profile.id] = user.diet_handler.amend_ratio_ref_calories(self._profile_calories[profile.id])

    def _calc_profile_ratios(self):
        """
        For each profile, calculates its ratio (not dish-related, global)
        """
        prof_calories = self.profile_calories
        user = self.user

        main_profile_calories = prof_calories[user.main_profile_id]

        self._profile_ratios = {}
        for key in prof_calories.keys():
            self._profile_ratios[key] = prof_calories[key] / main_profile_calories

    def split_ratios(self, total_ratio, profiles):
        """
        Given a dish total ratio  (final) and a list of profiles (eaters),
        return which part of ratio each profile should eat
        """
        prof_ratios = self.profile_ratios

        tot_eaters_ratios = sum(prof_ratios[p.id] for p in profiles)

        res = {}
        for p in profiles:
            res[p.id] = total_ratio * prof_ratios[p.id] / tot_eaters_ratios
        return res

    def get_main_profile_ratio(self):
        """
        Return the profile ratio for the main profile
        """
        return self.profile_ratios[self.user.main_profile_id]

    def get_main_ratio(self, total_ratio, profiles):
        """
        Given a dish total ratio (final) and a list of profiles (eaters),
        return how much the main profile should eat
        """
        splitted = self.split_ratios(total_ratio, profiles)
        return splitted[self.user.main_profile_id]

    def get_initial_ratios(self, days):
        """
        Given a list of days, return default ratios (theorically optimal)
        The calculation is done from profile_ratios and the meal structure
        @rtype: {dish_id: ratio}
        """
        res = {}
        for day in days:
            self._get_initial_day_ratios(day, res)
        return res

    def _get_initial_day_ratios(self, day, res):
        """
        Calculates initial ratios for dishes :
        - By calculating a day ratio : calories required by the user / how much calories are theorically brought by dishes
        - By applying profile ratios to each meal, depending on eaters
        """
        day_meal_slots = list(day.meal_slots.all())
        if len(day_meal_slots) == 0:
            return

        self._custom_mealslots = set() # List of meal slot ids that have at least a DT_CUSTOM or DT_EXTERNAL dish

        # Calculates :
        # - How many calories are "forced"
        # - How many calories are theorically brought by mutable dishes
        total_static_calories, day_structure_calories = self._calc_day_calories(day)

        # Calculating default ratios for the day
        main_profile_calories = self.profile_calories[self.user.main_profile_id]
        # Default ratio is the number of calories required by the user divided by
        # the theorical remaining structure calories
        day_ratio = float(main_profile_calories - total_static_calories) / day_structure_calories
        if ENABLE_DAY_RATIO_SECURITY:
            day_ratio = max(min(day_ratio, 2), 0.5)

        # Filling dish ratios by taking into account the eaters
        for meal_slot in day_meal_slots:
            meal_ratio = self._calc_meal_ratio(meal_slot, day_ratio)
            for dish in meal_slot.dishes.all():
                res[dish.id] = meal_ratio

    def _calc_day_calories(self, day):
        """
        Calculates :
        - How many calories are "forced"
        - How many calories are theorically brought by mutable dishes
        """
        total_static_calories = 0
        day_structure_calories = 0.
        # Calculating total calories on the given day for one profile
        for meal_slot in day.meal_slots.all():
            dishes = list(meal_slot.dishes.all())
            assert len(dishes) > 0
            for dish in meal_slot.dishes.all():
                static_calories, variable_calories = get_theoretical_dish_calories(dish)
                total_static_calories += static_calories
                day_structure_calories += variable_calories
                if dish.dish_type.has_static_ratio():
                    self._custom_mealslots.add(meal_slot.id)

        return total_static_calories, day_structure_calories

    def _calc_meal_ratio(self, meal_slot, day_ratio):
        """
        Given a mealslot, calculates the ratio of its dishes  (all the same by default)
        @param total_static_calories:
        """
        ms_eaters = list(meal_slot.eaters.all())
        prof_ratios = self.profile_ratios

        # Summing up the eaters ratios for this meal
        tot_prof_ratios = 0
        for eater in ms_eaters:
            tot_prof_ratios += prof_ratios[eater.profile_id]
        # Setting dish ratios (same for all dishes within the same mealslot, by default)
        if meal_slot.id in self._custom_mealslots:
            # Custom meals always have a ratio of 1
            assert len(ms_eaters) == 1, "Custom meal with more than one eater ?"
            return 1
        # Final ratio = day_ratio * eaters ratio
        res = day_ratio * tot_prof_ratios
        precision = self.precision_from_nb_eaters(len(ms_eaters))

        # Optimization for lunch/dinner balance. FIXME : do something more clever maybe ?
        if meal_slot.meal_type.key == "lunch":
            res *= 1.2
        elif meal_slot.meal_type.key == "dinner":
            res *= 0.8
        return max(0.5, round_to_closest(res, precision))

    @classmethod
    def precision_from_nb_eaters(cls, nb_eaters):
        """
        Return the precision that the ratios should have
        """
        # if nb_eaters == 1:
        #     return 0.25
        return 1

    def get_ratios_from_bdd(self, days):
        """
        Given a list of days, return the ratio for each dish
        @rtypê: {dish_id: ratio}
        """
        res = {}
        for dish_recipe in iter_dishrecipes(days):
            assert dish_recipe.dish_id not in res or res[dish_recipe.dish_id] == dish_recipe.ratio, "Inconsistant ratio into same dish"
            res[dish_recipe.dish_id] = dish_recipe.ratio
        return res


    def get_detailed_ratios_from_bdd(self, days):
        """
        Given a list of days, return the ratio for each dish, for each profile
        @rtypê: {dish_id: ratio}
        """
        res = {}
        for meal_slot in iter_mealslots(days):
            profiles = [eater.profile for eater in meal_slot.eaters.all()]
            for dish in meal_slot.dishes.all():
                for dish_recipe in dish.dishrecipe_set.all():
                    splitted = self.split_ratios(dish_recipe.ratio, profiles)
                    res[dish_recipe.dish_id] = splitted
                    break
        return res