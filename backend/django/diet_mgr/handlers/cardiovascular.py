
from django.utils                   import timezone
from math                           import ceil

from common.decorators              import overrides

from diet_mgr.handlers              import NonValidatedDietParametersException
from diet_mgr.handlers.base         import DietWithSlimDiagnosisMixin
from diet_mgr.handlers.slim         import AbstractSlimDiet

from emailing.tools                 import sendmail_template, MessageType

from hippocrate.models.constraints  import MealTypeBalanceConstraint, NutrientBalanceConstraint, NutrientMealTypeConstraint

from nutrient.models                import Nutrient

from optalim.config                 import Config

from planning_mgr.iterators         import iter_mealslots

from profile_mgr.models             import Profile, COMPUTE_IMC, COMPUTE_IMC_WEIGHT

import datetime

class CardiovascularDietHandler(DietWithSlimDiagnosisMixin, AbstractSlimDiet):
    """
    Diet that helps preventing cardiovascular issues
    """
    KEY = "cardiovascular"
    METABOLISM_UPDATE_INTERVAL  = datetime.timedelta(days = 7)  # Minimum interval to update metabolism value
    DIET_PARAMETERS             = {
        'normolipidic':     (int, True), # normolipidic qualitative (anticholesterol)
        'hyposodic':        (int, True), # Hypertension: sans-sel
        'low_trigly':       (int, True), # Régime contrôlé en glucides (diabète)
        'controlled_k':     (int, True), # contrôle des vitamines K
    }
    DIAGNOSIS_ARGUMENTS          = {'hypertension': int,
                                    'diabete':      int,
                                    'anticoagul':   int,
                                   }
    WEIGHT_REMINDER_INTERVAL    = datetime.timedelta(days=7)
    NUTRIENT_FAST_AMEND         = {}
    IMC_LIMIT_REFERENCE         = Profile.OVERWEIGHT_IMC
    CARDIO_DIET_COST_AMEND      = 50    # 5 times more important than other constraints -> priority
    GLUCIDE_VARIATION_TOLERANCE = 0.10  # 10% of variation allowed between two consecutive meals of the same type

    def validate_parameters(self, parameter_objs):
        return

    def amend_alcool(self, configuration):
        if self.parameters["low_trigly"] == 0:
            return configuration
        configuration['name'] = "alcool"
        configuration['unit'] = "g"
        configuration['max'] = 24 # More or less 2 glasses of wine per day
        configuration['cost'] = self.CARDIO_DIET_COST_AMEND
        configuration['daily_tolerance'] = 0
        return configuration

    def amend_vitamin_k(self, configuration):
        if self.parameters["controlled_k"] == 0:
            return configuration
        configuration['name'] = "K1+K2"
        configuration['unit'] = "µg"
        configuration['cost'] = self.CARDIO_DIET_COST_AMEND
        configuration['min'] = 45
        configuration['max'] = 50
        configuration['daily_tolerance'] = 10
        return configuration

    def amend_sodium(self, configuration):
        if self.parameters["hyposodic"] == 0:
            return configuration
        # Utilisation du régime hyposodé large (< 2400 mg)
        configuration['cost'] = self.CARDIO_DIET_COST_AMEND
        configuration['max'] = 2400
        return configuration

    def amend_cholesterol(self, configuration):
        if self.parameters["normolipidic"] == 0:
            return configuration
        configuration['name'] = "cholesterol"
        configuration['unit'] = "mg"
        configuration['cost'] = self.CARDIO_DIET_COST_AMEND
        configuration['max'] = 300
        configuration['unit'] = "mg"
        configuration['daily_tolerance'] = 0
        return configuration

    def amend_saturated_lipids(self, configuration):
        if self.parameters["normolipidic"] == 0:
            return configuration
        # Lipides totaux RNP par défaut: 35 à 40% des apports en énergie
        # Ici on veut 25% des lipides en acides gras saturés, ça nous donne 8 à 10% des apports en énergie
        configuration['cost'] = self.CARDIO_DIET_COST_AMEND
        configuration['min'] = 8
        configuration['max'] = 10
        configuration['mode'] = 'percentage_energy'
        return configuration

    def amend_monoinsaturated_lipids(self, configuration):
        if self.parameters["normolipidic"] == 0:
            return configuration
        # Lipides totaux RNP par défaut: 35 à 40% des apports en énergie
        # Ici on veut 50% des lipides en acides gras monoinsaturés, ça nous donne 17.5 à 20% des apports en énergie
        configuration['cost'] = self.CARDIO_DIET_COST_AMEND
        configuration['min'] = 17
        configuration['max'] = 20
        configuration['mode'] = 'percentage_energy'
        return configuration

    def amend_omega_6(self, configuration):
        if self.parameters["normolipidic"] == 0:
            return configuration
        else:
            return None # Désactivée suite à l'introduction d'une NutrientBalanceConstraint
        # Lipides totaux RNP par défaut: 35 à 40% des apports en énergie
        # Ici on veut 25% des lipides en acides gras polyinsaturés dont 80% d'omega 6, ça nous donne 6 à 8% des apports en énergie
        configuration['name'] = "acides gras polyinsaturés, 18:2 c,c n-6, linoléique, octadécadiénoïque"
        configuration['unit'] = "g"
        configuration['cost'] = self.CARDIO_DIET_COST_AMEND
        configuration['min'] = 6
        configuration['max'] = 8
        configuration['mode'] = 'percentage_energy'
        configuration['daily_tolerance'] = 20
        return configuration

    def amend_omega_3(self, configuration):
        if self.parameters["normolipidic"] == 0:
            return configuration
        else:
            return None # Désactivée suite à l'introduction d'une NutrientBalanceConstraint
        # Lipides totaux RNP par défaut: 35 à 40% des apports en énergie
        # Ici on veut 25% des lipides en acides gras polyinsaturés dont 20% d'omega 3, ça nous donne 1.75 à 2% des apports en énergie
        configuration['name'] = "omega3"
        configuration['unit'] = "g"
        configuration['cost'] = self.CARDIO_DIET_COST_AMEND
        configuration['min'] = 1.75
        configuration['max'] = 2
        configuration['mode'] = 'percentage_energy'
        configuration['daily_tolerance'] = 20
        return configuration

    def amend_fibres(self, configuration):
        if self.parameters["low_trigly"] == 0:
            return configuration
        configuration['name'] = "fibres alimentaires totales"
        configuration['unit'] = "g"
        configuration['cost'] = self.CARDIO_DIET_COST_AMEND
        configuration['min'] = 30
        del configuration['max']
        configuration['daily_tolerance'] = 0
        return configuration

    def amend_added_sugars(self, configuration):
        if self.parameters["low_trigly"] == 0:
            return configuration
        configuration['name'] = "sucres ajoutés"
        configuration['unit'] = "g"
        configuration['cost'] = self.CARDIO_DIET_COST_AMEND
        configuration['max'] = 7
        configuration['mode'] = 'percentage_energy'
        configuration['daily_tolerance'] = 0
        return configuration

    def amend_lipids(self, configuration):
        if self.parameters["low_trigly"] == 0:
            return configuration
        return None # Replaced by a constraint on glucids


    # def _amend_proteins_per_kg(self, configuration):
    #     if self.parameters["low_trigly"] == 1:
    #         # Removing the "slim" proteins policy for people with diabete.
    #         # It can conflicts with the other glucid/lipid/proteins distribution
    #         return None

    #     return self.amend_proteins_per_kg(configuration)

    def amend_fibres_per_kg(self, configuration):
        if self.parameters["low_trigly"] == 0:
            return configuration
        configuration['name'] = "fibres alimentaires totales"
        configuration['unit'] = "g"
        configuration['cost'] = self.CARDIO_DIET_COST_AMEND
        configuration['min'] = 15
        configuration['mode'] = 'per_1000kcal'
        configuration['daily_tolerance'] = 0
        return configuration

    def amend_glucids(self, configuration):
        if self.parameters["low_trigly"] == 0:
            return configuration
        configuration['name'] = "glucides totaux (par différence)"
        configuration['unit'] = "g"
        configuration['cost'] = self.CARDIO_DIET_COST_AMEND
        configuration['min'] = 50
        configuration['mode'] = 'percentage_energy'
        configuration['daily_tolerance'] = 5
        return configuration


    NUTRIENT_AMEND_FCNS = {
        # 'proteins_per_kg': _amend_proteins_per_kg,
        'alcool': amend_alcool,
        'vitamin_k': amend_vitamin_k,
        'sodium': amend_sodium,
        'fibres': amend_fibres,
        'cholesterol': amend_cholesterol,
        'lipids': amend_lipids,
        'lipids_saturated': amend_saturated_lipids,
        'lipids_monoinsaturated': amend_monoinsaturated_lipids,
        'omega6': amend_omega_6,
        'omega3': amend_omega_3,
        'added_sugar': amend_added_sugars,
        'fibres_per_kg': amend_fibres_per_kg,
        'glucides': amend_glucids
    }

    def get_base_weight(self):
        if COMPUTE_IMC(self.profile.weight, self.profile.height) > self.IMC_LIMIT_REFERENCE:
            return COMPUTE_IMC_WEIGHT(self.IMC_LIMIT_REFERENCE, self.profile.height)
        else:
            return self.profile.weight

    def _add_diabete_glucid_constraints(self, res, planning):
        """
        Adds to the list of constaints one constraint per meal_type,
        with the correct level of glucids
        """

        energy = round(self.compute_calories())
        glucids = energy * 0.5 / Config.energy_conversion["glucides totaux (par différence)"]  # 50% of energy is glucids. 1g = 4kcal

        meal_type_per_key = {}
        for meal_slot in iter_mealslots(planning.days.all()):
            meal_type_per_key[meal_slot.meal_type.key] = meal_slot.meal_type

        # How the glucids are distributed throughout the day, in percentage
        distribution = {"breakfast": 20.,
                        "morning_snack": 5.,
                        "lunch": 37.,
                        "snack": 5.,
                        "dinner": 33.}
        assert round(sum(distribution.values())) == 100

        for key in list(distribution.keys()):
            if key not in meal_type_per_key:
                # There is not such meal_type in the planning
                del distribution[key]

        # Make sure total is 100%
        nb_meal_types = len(distribution)
        redistribution = 100 - sum(distribution.values())
        for key in distribution.keys():
            distribution[key] += redistribution / nb_meal_types
        assert round(sum(distribution.values())) == 100

        for key, percentage in distribution.items():
            meal_type = meal_type_per_key[key]
            target_value = glucids * percentage / 100

            # Creating one NutrientMealTypeConstraint per meal_type
            res.append(NutrientMealTypeConstraint(
                Nutrient.get_nut("glucides"), meal_type, target_value * 0.9, target_value * 1.1,
                                  cost_per_percent_out=self.CARDIO_DIET_COST_AMEND))


    def build_nutrient_constraints(self, planning):
        res = super().build_nutrient_constraints(planning)
        if self.parameters["low_trigly"] != 0:
            # Adding specific constraints
            #res.append(MealTypeBalanceConstraint(
                #Nutrient.get_nut("glucides").id,
                #self.profile.id,
                #1 - self.GLUCIDE_VARIATION_TOLERANCE, # 90%
                #1 + self.GLUCIDE_VARIATION_TOLERANCE, # 110%
            #))
            res.append(NutrientBalanceConstraint(
                data_key = "glucides",
                referent_key = "energiekilocalories",
                min_ratio = 0.0,
                max_ratio = 0.7 / Config.energy_conversion["glucides totaux (par différence)"], # 1g glucid = 4kcal
                meal_constraint = True,
            ))
            self._add_diabete_glucid_constraints(res, planning)

        if self.parameters["normolipidic"] != 0:
            # res.append(NutrientBalanceConstraint(
                # Nutrient.get_nut("agmonoinsatures").id,
                # self.profile.id,
                # Nutrient.get_nut("lipides").id,
                # min_ratio = 0.45,
                # max_ratio = 0.55,
            # ))
            # res.append(NutrientBalanceConstraint(
                # Nutrient.get_nut("acidesgrassatures").id,
                # self.profile.id,
                # Nutrient.get_nut("lipides").id,
                # min_ratio = 0.22,
                # max_ratio = 0.28,
            # ))
            res.append(NutrientBalanceConstraint(
                "omega3",
                "omega6",
                min_ratio = 0.2,
                max_ratio = 0.3,
            ))
        return res

    def _diagnose(self, arguments):
        """
        Validate the arguments (raise NonValidatedDietParametersException if erroneous)
        And returns a diagnosis  ({key : value}, interpreted by AngularJS)
        """
        res = {
            'params': {},   # Parameters of diet (will be passed to subscription)
            'profile': {},  # Modifications on profile
            'other': {},    # Other (interpreted by AngularJS)
        }

        # If not explicitely given, we consider that normolipidic should be enabled
        if 'normolipidic' not in arguments:
            arguments['normolipidic']   = 1

        res['params']['hyposodic']      = arguments['hypertension']
        res['params']['low_trigly']     = arguments['diabete']
        res['params']['controlled_k']   = arguments['anticoagul']
        res['params']['normolipidic']   = arguments['normolipidic']

        current_height = self.profile.height
        current_weight = self.profile.weight

        if current_height is None or current_weight is None:
            raise NonValidatedDietParametersException("Merci d'indiquer vos poids et taille actuels")

        imc = COMPUTE_IMC(current_weight, current_height)

        res["other"]["overweight"] = 1 if imc > 25 else 0

        return res

