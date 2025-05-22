
from diet_mgr.handlers.base     import DietHandlerBase

from hippocrate.models.constraints      import NutrientConstraint

from optalim.config                     import Config

from nutrient.models                    import NutrientPack, Nutrient

from profile_mgr.models                 import Profile, COMPUTE_IMC, COMPUTE_IMC_WEIGHT

from optalim.log import logger
import copy

class AncStandardDiet(DietHandlerBase):
    """
    Standard diet with RNP recommendations
    """
    KEY = "balanced"
    NUTRIENT_FAST_AMEND = {} # Constraint key (anc.yml) -> dictionnary with values to update
    NUTRIENT_AMEND_FCNS = {} # Constraint key (anc.yml) -> method to amend the constraint description

    def __init__(self, *args ,**kargs):
        super().__init__(*args, **kargs)
        self.nutrients_per_name = dict((n.name, n) for n in  Nutrient.objects.all())

        self.enabled_nutrients_ids = set()
        for pack in self.profile.creator.nutrient_packs.all().prefetch_related('nutrients'):
            for nutrient in pack.nutrients.all():
                self.enabled_nutrients_ids.add(nutrient.pk)

    def get_base_weight(self):
        """
        Weight on which the 'per_kg' nutrient values are calculated
        """
        weight = self.profile.weight_or_default
        if COMPUTE_IMC(weight, self.profile.height_or_default) > Profile.OVERWEIGHT_IMC:
            # IMC bigger than 25 ? calculate calories from a IMC value of 25
            weight = COMPUTE_IMC_WEIGHT(Profile.OVERWEIGHT_IMC, self.profile.height_or_default)
        return weight

    def _parse_tolerance(self, tolerance_value):
        """
        From the configuration value of a tolerance, returning its definitive value
        """
        if tolerance_value == 'two_weekly_inputs_min' or tolerance_value == 'inf':
            return 1  # FIXME
        return float(tolerance_value) / 100

    def _load_nutrient_constraint(self, desc, energy, weight):
        """
        From a nutrient constraint configuration values (desc)
        Create a nutrient constraint object
        """
        try:
            nutrient = self.nutrients_per_name[desc['name']]
        except KeyError:
            for nutrient_name in self.nutrients_per_name.keys():
                logger.error("* %s" % nutrient_name)
            assert False, "Cannot find nutrient %s in database" % desc['name']

        min_value, max_value = -1, -1
        if 'min' in desc:
            min_value = desc['min']
        if 'max' in desc:
            max_value = desc['max']
        if 'objective' in desc:
            min_value, max_value = desc['objective'] - desc['variance'], desc['objective'] + desc['variance']

        assert 'unit' in desc, "No unit for nutrient constraint %s" % desc
        # Checking that nutrient has the correct unit
        assert nutrient.unit == desc['unit'],\
            "nutrient unit is different in DB and RNP config file : %s [DB: %s] [Conf: %s]" % (nutrient.name,
                                                                                                nutrient.unit,
                                                                                                desc['unit'])

        # Missing mode: assuming it's absolute values
        if 'mode' in desc:
            if desc['mode'] == 'percentage_energy':
                energy_conversion = Config.energy_conversion[nutrient.name]
                if min_value > 0: min_value = (energy / energy_conversion) * float(min_value) / 100
                if max_value > 0: max_value = (energy / energy_conversion) * float(max_value) / 100
            elif desc['mode'] == 'per_kg':
                if min_value > 0: min_value *= weight
                if max_value > 0: max_value *= weight
            elif desc['mode'] == 'per_1000kcal':
                if min_value > 0: min_value *= energy / 1000
                if max_value > 0: max_value *= energy / 1000
            else:
                assert False, "unknown nutrient mode: %s" % desc['mode']

        # Tolerance
        daily_tolerance_min = desc.get('daily_tolerance_min', 0)
        daily_tolerance_max = desc.get('daily_tolerance_max', 0)

        if 'daily_tolerance' in desc:
            assert daily_tolerance_min == 0 and daily_tolerance_max == 0, "cannot set min/max daily tolerance + global daily tolerance"
            daily_tolerance_min = daily_tolerance_max = desc['daily_tolerance']

        daily_tolerance_min = self._parse_tolerance(daily_tolerance_min)
        daily_tolerance_max = self._parse_tolerance(daily_tolerance_max)

        if nutrient.id not in self.enabled_nutrients_ids:
            cost = 0.05
        else:
            cost = desc['cost']

        return NutrientConstraint(nutrient, min_value, max_value,
                                  daily_tolerance_min=daily_tolerance_min,
                                  daily_tolerance_max=daily_tolerance_max,
                                  cost_per_percent_out=cost)

    def _amend_nutrients(self, data):
        """
        Modify the original RNP data
        """
        for key, update_values in self.NUTRIENT_FAST_AMEND.items():
            if update_values.get('delete', False):
                del data[key]
            else:
                data[key].update(update_values)
        for key, update_fcn in self.NUTRIENT_AMEND_FCNS.items():
            amended = update_fcn(self, data.get(key, dict()))
            if amended is None or len(amended) == 0:
                if key in data:
                    # Delete
                    del data[key]
            else:
                amended["key"] = key
                data[key] = amended
        return data

    def build_nutrient_constraints(self, planning):
        res = []

        age = self.profile.age
        if age < 20:
            age = 20 # FIXME: handle RNP for age < 20

        profile_data = None
        for item in Config.anc.values():
            if age >= item['min_age'] and\
               age <= item['max_age'] and\
               self.profile.sex == item['sex']:
                   # Match
                   profile_data = item
                   break
        else:
            assert False, "Couldn't match any profile in RNP file"

        energy = round(self.compute_calories())
        weight = self.get_base_weight()

        nutrients_data = self._amend_nutrients(copy.copy(profile_data['nutrients']))
        for key, nutri_desc in sorted(nutrients_data.items(), key=lambda x: x[0]):
            constraint = self._load_nutrient_constraint(nutri_desc, energy, weight)
            if constraint is not None:
                res.append(constraint)

        return res

