from nutrient.models            import Nutrient, NutrientCookAlteration, NutrientRawStateAlteration,\
                                       CookingMethodEffect
from recipe_mgr.models          import Food, Recipe, RawState, CookingMethod,\
                                       FoodType
from optalim.config             import Config
from optalim.settings           import TESTING
from django.core.cache          import cache
from collections                import defaultdict
import copy

ADD_ADDED_SUGAR = not TESTING

from optalim.log import logger

class NutrientCalculatorCache(object):
    """
    Contains cached infos about cooking method effects, food categories, raw state conversions, ...
    """
    __not_cooked_id   = None

    __nutrient_ids      = {}

    __cooking_method_effects = {}

    __nutrient_cook_alteration = None
    __nutrient_rawstate_alteration = None

    @classmethod
    def reset(cls):
        cls.__not_cooked_id   = None
        cls.__nutrient_ids    = {}
        cls.__cooking_method_effects = {}

        cls.__nutrient_cook_alteration = None
        cls.__nutrient_rawstate_alteration = None


    @classmethod
    def nutrient_cook_alteration(cls, nutrient_id, cooking_method_id):
        if cls.__nutrient_cook_alteration is None:
            cls.__nutrient_cook_alteration = defaultdict(dict)
            for nca in NutrientCookAlteration.objects.all():
                cls.__nutrient_cook_alteration[nca.nutrient_id][nca.cooking_method_id] = nca.ratio
        return cls.__nutrient_cook_alteration[nutrient_id][cooking_method_id]

    @classmethod
    def nutrient_rawstate_alteration(cls, nutrient_id, raw_state_id):
        if cls.__nutrient_rawstate_alteration is None:
            cls.__nutrient_rawstate_alteration = defaultdict(dict)
            for nra in NutrientRawStateAlteration.objects.all():
                cls.__nutrient_rawstate_alteration[nra.nutrient_id][nra.raw_state_id] = nra.ratio
        return cls.__nutrient_rawstate_alteration[nutrient_id][raw_state_id]

    @classmethod
    def not_cooked_id(cls):
        if not cls.__not_cooked_id:
            cls.__not_cooked_id = CookingMethod.objects.get(name="cru").id
        return cls.__not_cooked_id

    @classmethod
    def nutrient_id(cls, nutrient_name):
        if nutrient_name not in cls.__nutrient_ids:
            cls.__nutrient_ids[nutrient_name] = Nutrient.objects.get(name=nutrient_name).id
        return cls.__nutrient_ids[nutrient_name]

    @classmethod
    def cooking_method_effect(cls, food_type_id, cooking_method_id):
        if food_type_id not in cls.__cooking_method_effects:
            cls.__cooking_method_effects[food_type_id] = {}
            for cme in CookingMethodEffect.objects.filter(food_type_id=food_type_id):
                cls.__cooking_method_effects[food_type_id][cme.cooking_method_id] = cme
        return cls.__cooking_method_effects[food_type_id].get(cooking_method_id, None)

    @classmethod
    def init_added_sugars_food_types(cls):
        """
        Retrieve from the cache / or calculate and store
        The food types without added sugars :
        - fully_without: fruits & veggies
        - partly without: milk
        """
        cls.added_sugars_ftypes = cache.get('food_types:added_sugars')
        if cls.added_sugars_ftypes is None:
            FRUITS_VEGGIES = ["Fruits et jus de fruits", "Légumes et produits végétaux",
                              "Légumes", "Pommes de terre et apparentés", "Fruits"]
            MILK = ["Produits laitiers et d'oeufs", "Produits laitiers et entremets",
                    "Succédanés du lait", "Laits", "Aliments lactés diététiques",
                    "Yaourts et spécialités laitières type yaourts", "Fromages blancs ultrafrais"]

            cls.added_sugars_ftypes = {}

            for key, food_type_names in ('no_added_sugars', FRUITS_VEGGIES), ('partly_added_sugars', MILK):
                cls.added_sugars_ftypes[key] = [ft.id for ft in FoodType.objects.filter(name__in=food_type_names)]
                if not TESTING:
                    if len(cls.added_sugars_ftypes[key]) != len(food_type_names):
                        if FoodType.objects.count() == 0:
                            raise Exception("No foodtypes - please initialize a database with base data in it")
                        raise Exception("Food types are missing")

            cache.set('food_types:added_sugars', cls.added_sugars_ftypes, None)




class RecipeNutrientCalculator(object):
    """
    This class calculates the list of nutrients that a recipe
    has :
    * Weighing nutrients with grams of ingredients
    * Taking care of Cooking method and how it affects nutrients
    * Taking care of Raw state and how it affects nutrients
    """

    def __init__(self, recipe):
        self.recipe = recipe

        # Contains the sum of all ingredient nutrients
        self.aggregated_nutrients = defaultdict(float)

        self.cache = NutrientCalculatorCache()

        # For each nutrient, which amount of grams in the recipe contain data
        # for this nutrient.
        # E.g.: bread + butter  --  "vitamin c" is only available for bread, bread=50g, butter=10g
        # Then data availablity will be 83% (50g / 60g)
        self.nutrients_data_availability = defaultdict(float)

    def compute(self):
        """
        Calculate nutrients for this recipe
        """
        total_grams = 0
        for ingredient in self.recipe.ingredients.all():
            self.compute_ingredient_nutrients(ingredient)
            total_grams += ingredient.grams_without_loss

        if total_grams == 0:
            return self

        # Normalizing data availability
        for nutrient in self.nutrients_data_availability.keys():
            self.nutrients_data_availability[nutrient] /= total_grams

        # Add calculated nutrients
        AdditionalNutrientsCalculator(self.aggregated_nutrients, self.nutrients_data_availability, self.cache).apply()

        return self

    def retrieve_food_nutrients(self, ingredient):
        """
        Returns the nutrients values for a given food,
        indexed by cooking method (2nd dimension: raw state)
        and indexed by raw state (2nd dimension: cooking method)
        """
        per_cooking_method = defaultdict(lambda: defaultdict(set))
        per_raw_state      = defaultdict(lambda: defaultdict(set))

        food_nutrients = list(ingredient.food.food_nutrients.all())

        for food_nutrient in food_nutrients:
            per_cooking_method[food_nutrient.cooking_method_id][food_nutrient.raw_state_id].add(food_nutrient)
            per_raw_state[food_nutrient.raw_state_id][food_nutrient.cooking_method_id].add(food_nutrient)

        #logger.error("Missing nutrients for food %s" % food_id)

        return dict(per_cooking_method), dict(per_raw_state)


    def select_best_cooking_parameters(self, ingredient, nutrients_per_raw_state,
                                                         nutrients_per_cooking_method):
        """
        Given the ingredient, with its raw state and cooking method,
        Given what is available in the database as nutrient values,
        Return the (raw_state, cooking_method) tuple from which we'll calculate
        the final nutrient values.

        Ideally, these will be the ingredient raw state and cooking method, but
        these might not be available, in case we need to _calculate_ the effet from
        some values we have.

        @returns: (raw_state, cooking_method)
        """
        # Ideal options
        cooking_method, raw_state = ingredient.cooking_method_id, ingredient.raw_state_id

        # Lambdas for getting random cooking method from a raw state, and getting random raw state from a cooking method
        _random_cooking_method = lambda _raw_state: sorted(nutrients_per_raw_state[_raw_state].keys())[0]
        _random_raw_state = lambda _cooking_method: sorted(nutrients_per_cooking_method[_cooking_method].keys())[0]

        # First, looking if the nutrient database contains values for
        # food + cooking method + raw state
        if raw_state in nutrients_per_cooking_method.get(cooking_method, {}):
            return (raw_state, cooking_method)  # Hurray, we have the precise data!

        # Right, no FoodNutrient matches food + cooking_method + raw_state.
        # Is cooking method available with any raw state
        if cooking_method in nutrients_per_cooking_method:
            # Cooking method is available
            # Let's select the best raw state to calculate from
            if RawState.fresh_id() in nutrients_per_cooking_method[cooking_method]:
                # Our default is to calculate the cooking method from "fresh"
                return (RawState.fresh_id(), cooking_method)
            # Otherwise, pick any raw state  --  we'll revert the effect, and potentially apply an other one
            return (_random_raw_state(cooking_method), cooking_method)

        # Cooking method is not available at all - we'll manually calculate the effect
        # Let's see about the raw state
        if raw_state in nutrients_per_raw_state:
            # raw state is available with another cooking method
            # select the cooking method we'll be based upon
            if self.cache.not_cooked_id() in nutrients_per_raw_state[raw_state]:
                # Our default is to calculate the cooking method from "not cooked"
                return (raw_state, self.cache.not_cooked_id())
            # Otherwise, pick any way of cooking  --  we'll revert the cooking, and potentially apply an other one
            return raw_state, (_random_cooking_method(raw_state))

       # Damn we need to find a default raw state _AND_ a default cooking method, because no one exist for this food
        if self.cache.not_cooked_id() in nutrients_per_cooking_method:
            if RawState.fresh_id() in nutrients_per_cooking_method[self.cache.not_cooked_id()]:
                return (RawState.fresh_id(), self.cache.not_cooked_id())
            return (_random_raw_state(self.cache.not_cooked_id()), self.cache.not_cooked_id())
        if RawState.fresh_id() in nutrients_per_raw_state:
            return (RawState.fresh_id(), _random_cooking_method(RawState.fresh_id()))

        # completely random values
        raw_state = sorted(nutrients_per_raw_state.keys())[0]
        cooking_method = _random_cooking_method(raw_state)
        return raw_state, cooking_method


    def apply_cooking_method_weight_loss(self, nutrient_values, ingredient):
        """
        This method is called when:
        - The nutrient values for the wanted cooking method are available  (nutrient_id, amount_per_gram)
        - cooking method is not "NOT COOKED"
        - raw state is "FRESH"

        In this case, because nutrient values are expressed in "per gram cooked"
                  and because ingredients are always expressed in "per gram non-cooked"
                      , we need to calculate the weight loss during the cooking to get the right values
        @param nutrient_values: available nutrient values {nutrient_id: amount_per_gram}, expressed in "per gram cooked"
        @param ingredient: the ingredient for which we want to calculate the nutrients
        """

        food_type_id = ingredient.food.type_id
        if food_type_id is None:
            #logger.warning("Food %s has no type (which CookingMethodEffect then?)" % food_id)
            return
        else:
            cooking_method_effect = self.cache.cooking_method_effect(food_type_id, ingredient.cooking_method_id)
            if not cooking_method_effect:
                #logger.warning("No CookingMethodEffect for food category %s -- skipping" % food_category.category_id)
                return
        # Apply the weight loss ratio
        for nutrient_id in nutrient_values.keys():
            nutrient_values[nutrient_id] *= cooking_method_effect.weight_ratio


    def apply_cooking_method_effect(self, nutrient_values, from_cooking_method_id, ingredient):
        """
        Update the nutrient values by applying a modification from a food cooking method to another
        @param from_cooking_method_id: Cooking method which is available in the DB
        @param nutrient_values: List of (nutrient_id, amount_per_gram) for this cooking method
        @warning: nutrient_values will be modified
        @param ingredient: Ingredient for which we want to calculate the nutrients
        """

        if from_cooking_method_id != self.cache.not_cooked_id():
            #logger.warning("Reverting cooking method is not handled (yet?)")
            return

        # Calculating from "not_cooked", by applying NutrientCookAlteration
        for nutrient_id in nutrient_values.keys():
            # For each nutrient, applying effect of cooking method
            try:
                ratio = self.cache.nutrient_cook_alteration(nutrient_id, ingredient.cooking_method_id)
            except KeyError:
                #logger.warning("No NutrientCookAlteration for cooking method %s on nutrient %s -- skipping" %\
                                #(ingredient.cooking_method_id, nutrient_value.nutrient.id))
                continue

            nutrient_values[nutrient_id] *= ratio


    def apply_raw_state_effect(self, nutrient_values, from_raw_state_id, to_raw_state_id):
        """
        Update the nutrient values by applying a modification from a food raw state to another
        @param from_raw_state_id: Raw state which is available in the DB
        @param nutrient_values: List of (nutrient_id, amount_per_gram) for this raw state
        @warning: nutrient_values will be modified
        @param to_raw_state_id: Raw state in the ingredient for which we want to calculate the nutrients
        """
        if from_raw_state_id != RawState.fresh_id():
            logger.info("Reverting raw state is not handled (yet?)")
            return

        for nutrient_id in nutrient_values.keys():
            try:
                # For each nutrient, applying effect of raw state
                ratio = self.cache.nutrient_rawstate_alteration(nutrient_id, to_raw_state_id)
                nutrient_values[nutrient_id] *= ratio
            except KeyError:
                pass
                #logger.warning("No raw state alteration for raw state %i and nutrient %i" %\
                                    #(to_raw_state_id, nutrient_value.nutrient.id))


    def compute_ingredient_nutrients(self, ingredient):
        """
        For a given ingredient, calculates its nutrients
        """
        # Index properties per cooking method and raw states
        per_cooking_method, per_raw_state = self.retrieve_food_nutrients(ingredient)
        if len(per_cooking_method) == 0:
            if ingredient.food.has_nutrients:
                logger.critical("No nutrient on food %s (%s), but shoud have !" % (ingredient.food.name, ingredient.food.id))
            return

        # Given the available data, select raw state and cooking method
        # from which we'll calculate the final values (ideally, the ingredient raw state and cooking method)
        avail_raw_state_id, avail_cooking_method_id = self.select_best_cooking_parameters(ingredient, per_raw_state, per_cooking_method)

        # Apply the effect of raw state and cooking method on the nutrient values
        nutrient_values = per_cooking_method[avail_cooking_method_id][avail_raw_state_id]
        nutrient_values = dict((nv.nutrient_id, nv.amount_per_gram) for nv in nutrient_values)

        if avail_raw_state_id != ingredient.raw_state_id:
            # The raw state we want is not available, we need to calculate "manually" the effect
            self.apply_raw_state_effect(nutrient_values, avail_raw_state_id, ingredient.raw_state_id)

        if avail_cooking_method_id != ingredient.cooking_method_id:
            # The cooking method we want is not available, we need to calculate "manually" the effect
            self.apply_cooking_method_effect(nutrient_values, avail_cooking_method_id, ingredient)
        else:
            if ingredient.raw_state_id == RawState.fresh_id() and\
               ingredient.cooking_method_id != self.cache.not_cooked_id():
                # This ingredient is fresh and cooked, we need to calculate how the weight is affected by the cooking
                self.apply_cooking_method_weight_loss(nutrient_values, ingredient)

        # Applying quantity
        for nutrient_id in nutrient_values.keys():
            nutrient_values[nutrient_id] *= ingredient.grams_without_loss

        # Adding added sugars approximation
        self._add_added_sugars(nutrient_values, ingredient)

        for nutrient_id, amount in nutrient_values.items():
            # Adding the ingredient nutrient value to the total recipe
            self.aggregated_nutrients[nutrient_id] += amount
            # Increasing the percentage of nutrient matched by this recipe
            self.nutrients_data_availability[nutrient_id] += ingredient.grams_without_loss

    def _add_added_sugars(self, nutrient_values, ingredient):
        """
        From sugars and food_type, calculate "added sugars", approximately
        """
        if not ADD_ADDED_SUGAR:
            return
        food_type_id = ingredient.food.type_id
        sugar_id = Nutrient.get_nut('sucrestotaux').id
        added_sugar_id = Nutrient.get_nut('added_sugar').id

        sugar = nutrient_values.get(sugar_id, 0)

        if food_type_id in self.cache.added_sugars_ftypes['no_added_sugars']:
            added_sugar = 0
        elif food_type_id in self.cache.added_sugars_ftypes['partly_added_sugars']:
            # Approximation for milky food
            # Added sugar = sugar - 4% of ingredient grams
            added_sugar = max(0, sugar - 0.04 * ingredient.grams)
        else:
            added_sugar = sugar

        nutrient_values[added_sugar_id] = added_sugar




class AdditionalNutrientsCalculator(object):
    """
    This class is in charge of calculating nutrients from existing nutrients
    Those nutrients are defined in hippocrate/config/nutrient_calculations.yml
    """
    def __init__(self, nutrient_values, nutrient_availabilities, cache=None):
        """
        Takes into parameter a dictionnary {nutrient_id: value}
        and a NutrientCalculatorCache
        """
        if cache is None:
            self.cache = NutrientCalculatorCache()
        else:
            self.cache = cache

        self.nutrient_values = nutrient_values
        self.nutrient_availabilities = nutrient_availabilities

        self._equation_nutrient_ids = set()

    def apply(self):
        """
        Add into self.nutrient_values the calculated nutrients
        """
        if Config.nutrient_calculations is None:
            return
        for additional_nutri in Config.nutrient_calculations:

            self._equation_nutrient_ids = set()
            nutri_id = self.cache.nutrient_id(additional_nutri["name"])
            nutri_equation = copy.copy(additional_nutri)
            nutri_equation.pop("name")
            self.nutrient_values[nutri_id] = self._calculate(nutri_equation)

            # Calculating availability
            self.nutrient_availabilities[nutri_id] = sum(self.nutrient_availabilities[n] for n in self._equation_nutrient_ids) /\
                                                     len(self._equation_nutrient_ids)



    def _calculate(self, nutri_equation):
        """
        Recursively calculate an equation in nutrient_calculations.yml
        """
        if type(nutri_equation) in (float, int):
            return nutri_equation
        if type(nutri_equation) is str:
            # Nutrient name
            nutrient_id = self.cache.nutrient_id(nutri_equation)
            self._equation_nutrient_ids.add(nutrient_id)
            return self.nutrient_values[nutrient_id]
        # Operator
        assert len(nutri_equation) == 1, "multiple operators in equation ? %s" % nutri_equation
        operator, nodes = list(nutri_equation.items())[0]

        values = [self._calculate(node) for node in nodes]
        if operator == "sum":
            return sum(values)
        if operator == "minus":
            assert len(values) == 2, "minus with more or less than 2 members ? %s" % nutri_equation
            return values[0] - values[1]
        if operator == "division":
            assert len(values) == 2, "division with more or less than 2 members ? %s" % nutri_equation
            assert values[1] > 0, "dividing by 0 : %s" % nutri_equation
            return values[0] / values[1]
        if operator == "multiply":
            res = 1
            for val in values:
                res *= val
            return res
        assert False, "unknown operator : %s" % operator
