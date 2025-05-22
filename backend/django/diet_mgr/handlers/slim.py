
from django.utils               import timezone

from common.decorators          import overrides

from diet_mgr.handlers.anc      import AncStandardDiet
from diet_mgr.handlers.base     import MIN_REASONABLE_CALORIES, DietWithSlimDiagnosisMixin

from emailing.tools             import sendmail_template, MessageType

from hippocrate.models.filters  import ExcludeNonHealthyRecipesFilter

from profile_mgr.models         import Profile, COMPUTE_IMC, COMPUTE_IMC_WEIGHT

import datetime

class AbstractSlimDiet(AncStandardDiet):
    KEY = None

    def specific_filters(self):
        """
        Returns dynamically computed filters

        For slim diets : remove recipes perceived as "non-healthy"
        """
        return [ExcludeNonHealthyRecipesFilter()]

    def _calculate_diff_per_day(self, current_weight, previous_weight, nb_days):
        """
        Calculates difference between expected loss and real weight loss, per day
        """
        objective = self.get_base_weight()
        objective_loss = self.profile.weight - objective
        if objective_loss == 0:
            return 0

        diet_started_days_ago = (timezone.now() - self.profile.creator.diet_changed_at).days

        # Less than 3 kilos to lose  <>  280g per week
        expected_loss_per_day = self.EXPECTED_LOSS_PER_DAY_SMALL
        if objective_loss > 3: # More than 3 kilos to lose
            # 70g per day <> 500g per week
            expected_loss_per_day = self.EXPECTED_LOSS_PER_DAY_LARGE

        # What user is really losing recently, on a per day basis
        real_diff_per_day = (current_weight - previous_weight) / nb_days
        if real_diff_per_day > expected_loss_per_day:
            # Oh oh, not losing as much weight as expected
            return real_diff_per_day + expected_loss_per_day  # Returning difference with expected

        # Losing weight, that's great. But not too much ?
        if diet_started_days_ago < 14 and real_diff_per_day < 0:
            # Maximum weight loss during the beginning of the diet should be
            # 1kg per week if less than 3kg to lose, 1.3kg otherwise
            maximum_loss_per_day = -0.185 if objective_loss > 3 else -0.143
            if real_diff_per_day < maximum_loss_per_day:
                # Losing too quickly !
                return real_diff_per_day + abs(maximum_loss_per_day) # Returning difference with maximum

            # Losing reasonably, maybe more than expected, but ok bcse this is the beginning
            return 0 # That's all good

        return real_diff_per_day + expected_loss_per_day # Returning difference with expected.

    def compute_calories(self):
        objective = self.get_base_weight()
        if objective >= self.profile.weight:
            # Objective reached !
            return super().compute_calories()

        # Calculating calories for the objective
        theorical_caloric_need = self.profile.theorical_caloric_need(weight=objective)

        if not self.profile.forced_base_calories:
            # There is no external data source for standard calories
            # Use the theoretical objective
            caloric_need = theorical_caloric_need
        else:
            # There is a data provided
            # Let's calculate the diminution percentage based on theorical calculations
            # And apply it to the data provided
            theorical_base_caloric_need = self.profile.theorical_caloric_need()
            diminution_ratio = float(theorical_caloric_need) / theorical_base_caloric_need
            caloric_need = self.profile.caloric_need() * diminution_ratio

        # If less than 10kg of loss, -(10 - loss)%
        loss = self.profile.weight - objective
        if loss < 10:
            caloric_need = float(caloric_need * (100 - (10 - loss))) / 100
        return max(MIN_REASONABLE_CALORIES, caloric_need)

class SlimDietHandler(DietWithSlimDiagnosisMixin, AbstractSlimDiet):
    """
    Diet that helps losing weight (reducing calories, more proteins)
    """
    KEY = "slim"
    METABOLISM_UPDATE_INTERVAL   = datetime.timedelta(days=7) # Minimum interval to update metabolism value

    WEIGHT_REMINDER_INTERVAL     = datetime.timedelta(days=7)
    NUTRIENT_FAST_AMEND = {'lipids': {'cost': 100}, # Ensure lipid is a priority
                           'calories': {'cost': 100}, # Calories is a high priority constraint
                           'proteins': {'min': 15, 'max': 25, 'cost': 100},
                           }

    def get_base_weight(self):
        """
        Weight on which the 'per_kg' nutrient values are calculated
        """
        objective = self.parameters['objective']
        height = self.profile.height_or_default
        if COMPUTE_IMC(objective, height) > Profile.OVERWEIGHT_IMC:
            # IMC bigger than 25 ? calculate calories from a IMC value of 25
            objective = COMPUTE_IMC_WEIGHT(Profile.OVERWEIGHT_IMC, height)
        return objective

    @overrides(AncStandardDiet)
    def _apply_metabolism_correction(self, percentage):
        """
        When metabolism is modified, send an email to the user
        """
        percentage = super()._apply_metabolism_correction(percentage)
        if percentage < -0.01: # Modifying by more than 1%. Let's send an email
            nb_eaters = self.profile.creator.eaters.filter(regular=True).count()
            # We'll reduce quantities from now. Keep confidence !
            sendmail_template(MessageType.MAIN_INFO, 'diet_mgr/templates/slim_metabolism_reduction.html',
                        {'percentage': abs(int(percentage * 100)),
                         'nb_calories': self.compute_calories(),
                         'nb_eaters': nb_eaters}, "Votre régime a été modifié",
                        users=[self.profile.creator], send_async=True, tags=['metabolism_reduction'])
        elif percentage > 0.01:
            # You're going too fast :)
            pass

    def amend_ratio_ref_calories(self, value):
        """
        Modifies the main profile referent calories to calculate the ratio
        """
        # 80%
        if self.parameters['mode'] == 'eat_less':
            return value * 0.8
        return value
