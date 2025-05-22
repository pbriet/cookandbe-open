"""
This module contains the diet handlers. Their role is to
generate constraints for a given profile
"""
from datetime                           import timedelta
from math                               import ceil
from django.utils                       import timezone
from common.converters                  import convert
from common.date                        import today

from diet_mgr.models                    import Diet, UserDietParameter
from diet_mgr.handlers                  import NonValidatedDietParametersException, MissingDietParameter, InvalidDietParameterType, UnknownDietParameter
from hippocrate.models.filters          import TagRecipeFilter

from profile_mgr.models                 import Profile, COMPUTE_IMC, COMPUTE_IMC_WEIGHT

import numpy
import datetime

from optalim.log import logger

MIN_REASONABLE_CALORIES = 1500

class AutoDietRegisterMetaClass(type):
    """
    This metaclass is automatically registering the instanciated
    DietHandler in the Diet class (_handlers)
    """
    def __init__(cls, name, bases, dct):
        super(AutoDietRegisterMetaClass, cls).__init__(name, bases, dct)
        if dct.get('KEY', None):
            Diet.register_diet_handler(dct['KEY'], cls)

class DietHandlerBase(object, metaclass=AutoDietRegisterMetaClass):
    """
    This class describes how a diet should generate constraints
    """
    KEY                          = None
    METABOLISM_UPDATE_INTERVAL   = datetime.timedelta(days=15) # Minimum interval to update metabolism value
    DIET_PARAMETERS              = {} # {parameter_name : (parameter_type = 'number'/'string', is_mandatory)}
    DIAGNOSIS_ARGUMENTS          = {} # {argument_name: (argument_type = 'number'/'string')   Arguments required for diagnosis
    WEIGHT_REMINDER_INTERVAL     = datetime.timedelta(days=120)  # If weight is not updated during this period, ask the user to update it

    def __init__(self, diet, profile):
        self.diet    = diet
        self.profile = profile
        self._parameters = None

    @property
    def parameters(self):
        if self._parameters is None:
            self._parameters = self.load_parameters()
        return self._parameters

    def amend_ratio_ref_calories(self, value):
        """
        Modifies the main profile referent calories to calculate the ratio
        """
        return value

    def _get_last_metabolism_update(self):
        """
        Returns
        - the number of days since the metabolism has been last updated
        - the average weight over X days preceding this update
        """
        metabolism_last_values = self.profile.values.filter(metric__key = "metabolism").order_by("-time")
        metabolism_last_modif = None
        for val in metabolism_last_values:
            # Trying to detect when we last updated metabolism
            if round(val.float_value, 6) != round(self.profile.metabolism, 6):
                break
            metabolism_last_modif = val

        assert metabolism_last_modif is not None, "No metabolism values stored"

        if metabolism_last_modif.time > timezone.now() - self.METABOLISM_UPDATE_INTERVAL:
            # Metabolism has been updated too recently. We need more time.
            return None
        return metabolism_last_modif.time

    def _get_avg_weight_before(self, weights, t, get_previous_if_missing=False):
        """
        Returns the average weight measures X days before t (including t)
        """
        min_date = t - self.METABOLISM_UPDATE_INTERVAL
        interval_weights = [w.float_value for w in weights if
                                       w.time >= min_date and\
                                       w.time <= t]

        if len(interval_weights) == 0:
            # No weight measure within the time window
            if get_previous_if_missing:
                values = self.profile.values.filter(metric__key = "metabolism", time__lt=min_date).order_by("-time")[:0]
                if len(values) == 0:
                    return None
                return values[0].float_value
            return None

        return numpy.mean(interval_weights)

    def _same_weight_trend(self, last_metabolism_update, last_update_avg_weight,
                                 current_avg_weight):
        """
        Checking that the weight is evolving in the same direction for a while
        W0 -> W1 -> W2

        Precisely : check that the weight values in the interval ]last_metabolism_update; now() - X days[ are between
                    last_update_avg_weight and current_avg_weight
        """
        weight_values_between = self.profile.values.filter(metric__key="weight",
                                                           time__gt=last_metabolism_update,
                                                           time__lt=timezone.now() - self.METABOLISM_UPDATE_INTERVAL)
        weight_values_between = list([w.float_value for w in weight_values_between])
        if len(weight_values_between) == 0:
            return False # There has been no weight measure between now - X days, and last metabolism update

        avg_between = numpy.mean(weight_values_between)

        # Is avg_between... between ?
        return (avg_between > last_update_avg_weight) == (avg_between < current_avg_weight)

    def _apply_metabolism_correction(self, percentage):
        """
        Modify the value of metabolism by applying a correction percentage (e.g 5% or 10%)
        """
        nb_calories = self.compute_calories()
        if nb_calories <= MIN_REASONABLE_CALORIES:
            # Already at the minimum
            return 0
        if nb_calories * (1 + percentage) < MIN_REASONABLE_CALORIES:
            # Reaching minimum calories by modifying
            percentage = float(MIN_REASONABLE_CALORIES) / float(nb_calories) - 1
        self.profile.metabolism *= 1 + percentage
        self.profile.metabolism = max(min(self.profile.metabolism, 1.3), 0.7)
        self.profile.save()
        return percentage

    def update_metabolism(self):
        """
        cf email discussion 15/09/2014 :
        --> La dernière modification du métabolisme a-t-elle eu lieu il y a plus de 15 jours ?  [7 pour régime minceur/prise de poids]
        -----> oui
        -----> Sur les 15/7 derniers jours, récupération des 3 derniers relevés de poids (ou moins s'il n'y a pas eu 3 relevés). Moyenne.
        -----> Récupération des 3 derniers relevés précédent la dernière mise à jour du métabolisme (ou moins - idem). Moyenne.
        -----> variation > 90g/j : +/- 15%
        -----> variation > 60g/j : +/- 10%
        -----> variation > 30g/j : +/- 5%
        -----> variation < 30g/j
        -----------> Y-a-t-il eu variation > 800g en valeur absolue depuis la dernière mise à jour du métabolisme ?
        -----------> oui : +/- 2%
        ----------->  non : Y-a-t-il eu variation > 400g en valeur absolue depuis la dernière mise à jour du métabolisme ?
        ---------------> oui. Est-ce qu'il s'agit d'une deuxième prise/perte de poids consécutive
        ---------------------> oui : +/- 2%
        """
        last_metabolism_update = self._get_last_metabolism_update()
        if last_metabolism_update is None:
            return # Updated too recently

        # Retrieving all weight values (date descending) from last update - 2*interval
        weight_data = list(self.profile.values.filter(metric__key = "weight",
                                                      time__gte=last_metabolism_update - 2*self.METABOLISM_UPDATE_INTERVAL).order_by('-time'))

        # Weight average in the X days before last metabolism update
        last_update_avg_weight = self._get_avg_weight_before(weight_data, last_metabolism_update, get_previous_if_missing=True)
        if last_update_avg_weight is None:
            # There was no data X days before
            return

        # Weight average in the last X days
        current_avg_weight = self._get_avg_weight_before(weight_data, timezone.now())
        assert current_avg_weight is not None, "Metabolism update called with no weight modification within the last %i days ?" % self.METABOLISM_UPDATE_INTERVAL

        nb_days = (timezone.now() - last_metabolism_update).days
        # Calculating difference between expected loss (default 0) and real weight loss, per day
        diff_per_day = self._calculate_diff_per_day(current_avg_weight, last_update_avg_weight, nb_days)

        # We reduce the metabolism if there is weight gained, and increase it if there is weight loss
        diff_coeff = -1 if diff_per_day > 0 else 1
        # From weight_diff, duration and current metabolism --> update value
        if abs(diff_per_day) > 0.09:
            # More than 90g difference per day
            self._apply_metabolism_correction(0.15 * diff_coeff)
        elif abs(diff_per_day) > 0.06:
            # More than 60g difference per day
            self._apply_metabolism_correction(0.10 * diff_coeff)
        elif abs(diff_per_day) > 0.03:
            # More than 30g difference per day
            self._apply_metabolism_correction(0.05 * diff_coeff)
        elif nb_days * abs(diff_per_day) > 0.8:
            # More than 800g weight difference, but slowly -> small correction
            self._apply_metabolism_correction(0.02 * diff_coeff)
        elif nb_days * abs(diff_per_day) > 0.4 and self._same_weight_trend(last_metabolism_update, last_update_avg_weight,
                                                                           current_avg_weight):
            # More than 400g weight difference, the second time at least -> small correction
            self._apply_metabolism_correction(0.02 * diff_coeff)

    def _calculate_diff_per_day(self, current_weight, previous_weight, nb_days):
       """
       Calculates difference between expected loss (default 0) and real weight loss, per day
       """
       return (current_weight - previous_weight) / nb_days

    def compute_calories(self):
        """
        Returns the amount of calories suited for this profile
        """
        return max(MIN_REASONABLE_CALORIES, self.profile.caloric_need())

    def diagnose(self, parameter_dict):
        """
        From raw parameters, returns a diagnostic
        """
        converted_args = self._get_diagnosis_arguments(parameter_dict)
        return self._diagnose(converted_args)

    def _diagnose(self, arguments):
        """
        From the validated and converted dictionnary  {argument -> value}
        returns a diagnostic (dictionary, interpreted by frontend)
        """
        raise NotImplementedError

    def _get_diagnosis_arguments(self, parameter_dict):
        """
        From a {parameter_name -> parameter_value} dictionnary,
        returns the same, but with values converted.
        Checks that all the values are given
        """
        res = {}
        for p_name, p_type in self.DIAGNOSIS_ARGUMENTS.items():
            value = parameter_dict.get(p_name, None)
            if value is None:
                # Parameter is mandatory but not provided
                raise MissingDietParameter(p_name)
            try:
                value = convert(value, p_type)
            except ValueError:
                # Cannot convert the value as expected
                raise InvalidDietParameterType(p_name)
            res[p_name] = value
        return res

    def _build_userdiet_parameters(self, parameter_dict):
        """
        From a {parameter_name -> parameter_value} dictionnary,
        build UserDietParameter objects and return them
        """
        new_parameters_objs = {}

        for p_name, p_options in self.DIET_PARAMETERS.items():
            p_type, p_mandatory  = p_options
            value = parameter_dict.get(p_name, None)

            if p_mandatory and value is None:
                # Parameter is mandatory but not provided
                raise MissingDietParameter(p_name)
            if value is not None:
                try:
                    value = convert(value, p_type)
                except ValueError:
                    # Cannot convert the value as expected
                    raise InvalidDietParameterType(p_name)

                parameter_obj = UserDietParameter(user=self.profile.creator, name=p_name)
                if p_type in (int, float):
                    parameter_obj.float_value = value
                else:
                    assert p_type is str, "parameter type can only be int, float or str"
                    parameter_obj.string_value = value

                new_parameters_objs[p_name] = parameter_obj
        return new_parameters_objs

    def save_parameters(self, parameter_dict):
        """
        From a {parameter_name -> parameter_value} dictionnary,
        check its validity for the given diet, and save them as UserDietParameters (replacing the previous UserDietParameters)
        """
        unknown_parameters = set(parameter_dict.keys()).difference(self.DIET_PARAMETERS.keys())
        if len(unknown_parameters):
            # Parameter is not listed in DIET_PARAMETERS
            raise UnknownDietParameter(unknown_parameters.pop())

        new_parameters_objs = self._build_userdiet_parameters(parameter_dict)

        # Validation part (optional)
        self.validate_parameters(new_parameters_objs)

        # Deleting existing diet paremters
        self.profile.creator.diet_parameters.all().delete()

        # Saving new ones
        UserDietParameter.objects.bulk_create(new_parameters_objs.values())

    def validate_parameters(self, parameter_objs):
        """
        @parameter_objs: dict { parameter_name -> UserDietParameter object }
        raise a NonValidatedDietParametersException
        """
        pass

    def load_parameters(self):
        """
        Load the user diet parameters, and return them in a dictionnary {name: value}
        """
        res = {}

        for udiet_parameter in self.profile.creator.diet_parameters.all():
            if udiet_parameter.float_value is not None:
                res[udiet_parameter.name] = udiet_parameter.float_value
            else:
                res[udiet_parameter.name] = udiet_parameter.string_value
        return res

    def filters(self):
        """
        Returns the list of filters to apply
        """
        if self.diet.included_food_tags.count() > 0:
            logger.warning("Diet food tag inclusion is not handled yet")

        for food_tag in self.diet.excluded_food_tags.all():
            yield TagRecipeFilter(self.profile, food_tag, critical = True)

        yield from self.specific_filters()

    def specific_filters(self):
        """
        Returns dynamically computed filters
        """
        return []

    def build_nutrient_constraints(self, planning):
        raise NotImplementedError

    def validate_constraint(self, constraint):
        return constraint

    def update_metaplanning(self, user):
        """
        Override this method to apply diet-specific modifications on user metaplanning when selecting the diet
        """
        pass


class DietWithSlimDiagnosisMixin:
    DIAGNOSIS_ARGUMENTS = {
       'objective': int,
       'snacking':  int, # Does this person is "snacking" often (1) or not (0)
       'diet_past': int, # How many slim diets have been followed in the past
       'genetic'  : int, # Is there some genetic tendency to be fat (1 = yes, 0 = no)
    }
    DIET_PARAMETERS = {
        'objective': (int, True),  # Objective weight
        'mode'     : (str, True) # Either 'eat_less', or 'eat_different'
    }


    EXPECTED_LOSS_PER_DAY_SMALL  = 0.04 # Expected loss per day (in kilos) for people losing less than 3kos
    EXPECTED_LOSS_PER_DAY_LARGE  = 0.07 # Expected loss per day (in kilos) for people losing more than 3kos

    def validate_parameters(self, parameter_objs):
        """
        @parameter_objs: dict { parameter_name -> UserDietParameter object }
        raise a NonValidatedDietParametersException

        Ensure that IMC is correct
        """
        current_height = self.profile.height
        current_weight = self.profile.weight

        if current_height is None or current_weight is None:
            raise NonValidatedDietParametersException("Merci d'indiquer vos poids et taille actuels")

        objective_weight = parameter_objs['objective'].float_value

        if current_weight <= objective_weight:
            raise NonValidatedDietParametersException("Merci d'indiquer un poids objectif inférieur à votre poids actuel")


    def _diagnose(self, arguments):
        """
        Validate the arguments (raise NonValidatedDietParametersException if erroneous)
        And returns a diagnosis  ({key : value}, interpreted by AngularJS)
        """
        current_height = self.profile.height
        current_weight = self.profile.weight

        if current_height is None or current_weight is None:
            raise NonValidatedDietParametersException("Merci d'indiquer vos poids et taille actuels")

        current_imc = COMPUTE_IMC(current_weight, current_height)

        if current_imc <= Profile.THIN_IMC:
            raise NonValidatedDietParametersException("Votre IMC actuel est inférieur à %s (maigreur). Une perte de poids pourrait porter atteinte à votre santé. Contactez votre médecin." % Profile.THIN_IMC)

        final_objective = arguments['objective']

        if current_weight <= final_objective:
            raise NonValidatedDietParametersException("Merci d'indiquer un poids objectif inférieur à votre poids actuel")

        # Maximum objective is -15% of weight, or IMC=18.5
        max_objective = ceil(max(0.85 * current_weight, COMPUTE_IMC_WEIGHT(Profile.THIN_IMC, current_height)))

        res = {'questions': arguments,
               'params': {},   # Parameters of diet (will be passed to subscription)
               'profile': {},  # Modifications on profile
               'other': {}     # Other (interpreted by AngularJS)
               }

        if final_objective < max_objective:
            final_objective = max_objective
            res['other']['objective_non_reasonable'] = True
            res['other']['original_objective'] = arguments['objective']

        res['params']['objective'] = final_objective

        metabolism = 1  # Weakness here : we lose the metabolism "history", if existing user.
                        # But restarting from existing might lead to "cumulative" metabolism
                        # I.e. 3 times subscribing to slim diet will accumulate the metabolism reduction
                        # coefficients. The current way is less risky.

        if arguments['diet_past'] >= 10:
            metabolism *= 0.7
        elif arguments['diet_past'] >= 5:
            metabolism *= 0.8
        elif arguments['diet_past'] >= 1:
            metabolism *= 0.9

        if arguments['genetic'] == 1:
            # Family is used to gain weight easily :
            # Reduce metabolism
            metabolism *= 0.9

        res['profile']['metabolism'] = round(metabolism, 2)

        if arguments['snacking'] == 1:
            res['params']['mode'] = 'eat_different'
        else:
            res['params']['mode'] = 'eat_less'

        loss = current_weight - final_objective
        if loss > 3:
            loss_per_day = self.EXPECTED_LOSS_PER_DAY_LARGE
        else:
            loss_per_day = self.EXPECTED_LOSS_PER_DAY_SMALL

        res['other']['estimated_date'] = today() + datetime.timedelta(days=ceil(loss / loss_per_day))

        return res

