from hippocrate_cpp.core                import UnicityConstraint        as UnicityConstraintC,\
                                           RedundancyConstraint     as RedundancyConstraintC,\
                                           NutrientConstraint       as NutrientConstraintC,\
                                           TimeConstraint           as TimeConstraintC,\
                                           BudgetConstraint         as BudgetConstraintC,\
                                           MaxModifsConstraint      as MaxModifsConstraintC,\
                                           UnicityFoodTagConstraint as UnicityFoodTagConstraintC,\
                                           MealBalanceConstraint    as MealBalanceConstraintC

from hippocrate_cpp.core                import MealTypeBalanceConstraint    as MealTypeBalanceConstraintC
from hippocrate_cpp.core                import NutrientBalanceConstraint    as NutrientBalanceConstraintC
from hippocrate_cpp.core                import NutrientMealTypeConstraint   as NutrientMealTypeConstraintC
from hippocrate_cpp.core                import ShoppingConstraint           as ShoppingConstraintC
from hippocrate_cpp.core                import BudgetConstraint             as BudgetConstraintC
from hippocrate_cpp.core                import RecipesPenaltiesConstraint  as RecipesPenaltiesConstraintC

from hippocrate_cpp.core                import NutrientWeekRule, NutrientDayRule,\
                                           DayNutrientBalanceRule, MealNutrientBalanceRule,\
                                           UnicityRule, NutrientMealRule

from hippocrate_cpp.core                import IdVector
from hippocrate.models.database     import Nutrient
from common.boost                   import to_dict
import re



class BaseConstraintPy(object):

    INDEX = {} # Way of indexing the Rules in the logs/returns client-side

    def is_nutrient_related(self):
        return False

    def cost(self, score):
        return score.by_constraint_id[self.id]

    def rule_cost(self, score, rule):
        return score.by_rule_id[rule.id]


    def to_planning_indicator(self, solution, score):
        """
        Serialize the constraint for returning indicators data to planning
        """
        total_cost = 0
        for rule in self.rules:
            total_cost += self.rule_cost(score, rule)

        flag = "ko" if total_cost > 50 else "ok"

        return {"key": self.key,
                "cost": total_cost,
                "enabled": True,
                "flag": flag,
                "type": "simple"}


    def overall_success(self, solution, score):
        """
        Returns a text that describes how the objective is reached (or not reached)
        """
        if self.cost(score) == 0:
            return "Succès"
        return "Echec"

    @property
    def key(self):
        raise NotImplementedError


    def other_infos(self, solution, score):
        """
        Returns some other infos for the frontend
        """
        return {}

    def details_per_day(self, problem, solution, score):
        """
        Returns details per day (to be displayed on the planning)
        """
        return {}

    def details_per_meal(self, solution, score):
        """
        Returns details per meal (to be displayed on the planning)
        """
        return {}

    def details_per_dish(self, problem, solution, score):
        """
        Returns details per dish (to be displayed on the planning)
        """
        return {}

class TimeConstraint(TimeConstraintC, BaseConstraintPy):

    INDEX = {'all': {'main_index':        'per_meal',
                     'index_attr':      'meal_id',
                     'secondary_index': None}
    }

    def __init__(self, *args, **kargs):
        TimeConstraintC.__init__(self, *args, **kargs)

    @property
    def key(self):
        return "time"

    def overall_success(self, solution, score):
        """
        Returns a text that describes how the objective is reached (or not reached)
        """
        if self.cost(score) == 0:
            return "Tous les repas suggérés sont dans la limite de temps"
        return "Le temps est en excès sur la semaine"

    def details_per_meal(self, solution, score):
        res = {}
        for rule in self.rules:
            meal_id = rule.meal_id
            cost = score.by_rule_id[rule.id]
            res[meal_id] = {'description': "", 'cost': cost,
                            'flag': 'ko' if cost > 0 else 'ok'}
        return res


class RecipesPenaltiesConstraint(RecipesPenaltiesConstraintC, BaseConstraintPy):

    INDEX = {'all': {'main_index':       'global',
                    'index_attr':      None,
                    'secondary_index': None}
    }

    def __init__(self, *args, **kargs):
        RecipesPenaltiesConstraintC.__init__(self, *args, **kargs)

    @property
    def key(self):
        return "recipe_penalities"


class BudgetConstraint(BudgetConstraintC, BaseConstraintPy):

    INDEX = {'all': {'main_index':       'global',
                    'index_attr':      None,
                    'secondary_index': None}
    }

    def __init__(self, *args, **kargs):
        BudgetConstraintC.__init__(self, *args, **kargs)

    @property
    def key(self):
        return "budget"

    def overall_success(self, solution, score):
        """
        Returns a text that describes how the objective is reached (or not reached)
        """
        if self.cost(score) == 0:
            return "Budget maitrisé"
        return "Budget en excès"

class UnicityConstraint(UnicityConstraintC, BaseConstraintPy):

    INDEX = {UnicityRule: {'main_index':      'global',
                           'index_attr':      None,
                           'secondary_index': None}
    }

    def __init__(self, cost, week_dish_type_ids, day_dish_type_ids=None):
        wk_dt_ids = IdVector()
        for dt_id in week_dish_type_ids: wk_dt_ids.append(dt_id)
        day_dt_ids = IdVector()
        if day_dish_type_ids:
            for dt_id in day_dish_type_ids: day_dt_ids.append(dt_id)
        super().__init__(cost, wk_dt_ids, day_dt_ids)

    @property
    def key(self):
        return "unicity"

    def overall_success(self, solution, score):
        """
        Returns a text that describes how the objective is reached (or not reached)
        """
        nb_redundancies = self.nb_redundancies(solution)
        if nb_redundancies == 0:
            return "Recettes variées"
        return "Seulement %i redondances" % nb_redundancies

class RedundancyConstraint(RedundancyConstraintC, BaseConstraintPy):
    INDEX = {'all': {'main_index':       'global',
                    'index_attr':      None,
                    'secondary_index': None}
    }

    def __init__(self, cost, dish_type_ids, *args, **kargs):
        dt_ids = IdVector()
        for dt_id in dish_type_ids: dt_ids.append(dt_id)
        super().__init__(cost, dt_ids, *args, **kargs)

    @property
    def key(self):
        return "redundancy"

    def overall_success(self, solution, score):
        """
        Returns a text that describes how the objective is reached (or not reached)
        """
        nb_weak_dishids = len(self.get_weak_dishids(solution))
        if nb_weak_dishids == 0:
            return "Redondance optimale"
        return "%i plats pas suffisamment redondants" % nb_weak_dishids

class ShoppingConstraint(ShoppingConstraintC, BaseConstraintPy):
    INDEX = {
        'all': {
            'main_index':       'global',
            'index_attr':      None,
            'secondary_index': None,
        }
    }

    @property
    def key(self):
        return "shopping"

    def overall_success(self, solution, score):
        """
        Returns a text that describes how the objective is reached (or not reached)
        """
        nb_items = self.nb_items(solution)
        if nb_items <= self.items_limit:
            return "Liste de course optimale"
        return "Liste de course trop longue (%i / %i)" % (nb_items, self.items_limit)

class UnicityFoodTagConstraint(UnicityFoodTagConstraintC, BaseConstraintPy):

    INDEX = {'all': {'main_index':       'per_day',
                    'index_attr':      'day_id',
                    'secondary_index': None}
    }

    @property
    def key(self):
        return "food_tag_unicity"

    def details_per_dish(self, problem, solution, score):
        res = {}
        for dish_id in self.get_weak_dishids(solution):
            res[dish_id] = {'description': "XXX",
                            'flag': 'ko'}
        return res

    def overall_success(self, solution, score):
        """
        Returns a text that describes how the objective is reached (or not reached)
        """
        nb_redundancies = self.nb_redundancies(solution)
        if nb_redundancies == 0:
            return "Recettes variées"
        return "Seulement %i redondances" % nb_redundancies

class MaxModifsConstraint(MaxModifsConstraintC, BaseConstraintPy):

    INDEX = {'all': {'main_index':       'global',
                    'index_attr':      None,
                    'secondary_index': None}
    }

    @property
    def key(self):
        return "maxmodifs"

    def overall_success(self, solution, score):
        """
        Returns a text that describes how the objective is reached (or not reached)
        """
        return "%i modifications" % self.nb_modifs(solution)

class MealBalanceConstraint(MealBalanceConstraintC, BaseConstraintPy):

    INDEX = {'all': {'main_index':       'per_day',
                    'index_attr':      'day_id',
                    'secondary_index': None}
    }

    @property
    def key(self):
        return "meal_balance"

    def is_nutrient_related(self):
        return True

    def overall_success(self, solution, score):
        """
        Returns a text that describes how the objective is reached (or not reached)
        """
        return "(non disponible - todo)"

class MealTypeBalanceConstraint(MealTypeBalanceConstraintC, BaseConstraintPy):

    INDEX = {'all': {'main_index':       'per_mealtype',
                    'index_attr':      'meal_type_id',
                    'secondary_index': None}
    }

    @property
    def key(self):
        return "meal_type_balance"

    def is_nutrient_related(self):
        return True

    def overall_success(self, solution, score):
        """
        Returns a text that describes how the objective is reached (or not reached)
        """
        return "(non disponible - todo)"

class NutrientBalanceConstraint(NutrientBalanceConstraintC, BaseConstraintPy):

    INDEX = {DayNutrientBalanceRule: {'main_index':       'per_day',
                                            'index_attr':     'day_id',
                                            'secondary_index': 'nutrients'},
             MealNutrientBalanceRule: {'main_index':       'per_meal',
                                            'index_attr':      'meal_id',
                                            'secondary_index': 'nutrients'},
    }

    @property
    def key(self):
        return "nutrient_balance"

    def is_nutrient_related(self):
        return True

    def overall_success(self, solution, score):
        """
        Returns a text that describes how the objective is reached (or not reached)
        """
        return "(non disponible - todo)"

class NutrientMealTypeConstraint(NutrientMealTypeConstraintC, BaseConstraintPy):
    INDEX = {NutrientMealRule: {'main_index': 'per_day',
                                      'index_attr': 'day_id',
                                      'secondary_index': 'mealtype_nutrients'}}

    def __init__(self, nutrient, meal_type, *args, **kargs):
        self.nutrient = nutrient
        self.meal_type = meal_type
        NutrientMealTypeConstraintC.__init__(self, nutrient.key, self.meal_type.id, *args, **kargs)

    def is_nutrient_related(self):
        return True

    @property
    def key(self):
        return self.nutrient.key + '_' + self.meal_type.key

class ProteinsConstraint(NutrientConstraintC, BaseConstraintPy):
    """
    Constraint on proteins
    """
    INDEX = {NutrientWeekRule: {'main_index':       'global',
                                'index_attr':     None,
                                'secondary_index': 'proteins'},
             NutrientDayRule:  {'main_index':       'per_day',
                                'index_attr':      'day_id',
                                'secondary_index': 'proteins'},
    }

    def __init__(self, proteins_key, *args, **kargs):
        self.proteins_key = proteins_key
        NutrientConstraintC.__init__(self, proteins_key, *args, **kargs)

    @property
    def key(self):
        return self.proteins_key

class NutrientConstraint(NutrientConstraintC, BaseConstraintPy):

    INDEX = {NutrientWeekRule: {'main_index':       'global',
                                'index_attr':     None,
                                'secondary_index': 'nutrients'},
             NutrientDayRule:  {'main_index':       'per_day',
                                'index_attr':      'day_id',
                                'secondary_index': 'nutrients'},
    }
    def __init__(self, nutrient, *args, **kargs):
        self.nutrient = nutrient
        if 'daily_tolerance' in kargs:
            kargs['daily_tolerance_min'] = kargs['daily_tolerance_max'] = kargs.pop('daily_tolerance')
        NutrientConstraintC.__init__(self, nutrient.key, *args, **kargs)

    def is_nutrient_related(self):
        return True

    @property
    def key(self):
        return self.nutrient.key

    @property
    def enabled(self):
        return self.cost_per_percent_out > 0.5

    def to_planning_indicator(self, solution, score):
        """
        Serialize the constraint for returning indicators data to planning
        """
        res = super().to_planning_indicator(solution, score)
        del res['flag'] # Flag is calculated through API given daily and weekly data

        res['type'] = 'min_max'
        res['enabled'] = self.enabled
        res["cost_per_percent_out"] = self.cost_per_percent_out
        res['daily'] = {}


        for rule in self.rules:
            nutrient_value = rule.get_value(solution)
            if isinstance(rule, NutrientWeekRule):
                data = self.get_details_with_value(rule, score, nutrient_value / rule.nb_days)
                res['weekly'] = data
            else:
                data = self.get_details_with_value(rule, score, nutrient_value, is_day=True)
                res['daily'][str(rule.day_id)] = data


        if len(res['daily']) == 0:
            del res['daily']

        return res



    def other_infos(self, solution, score):
        week_nutrient_value = self._get_avg_week_value(solution, score)

        return {"min": round(self.min_value, 2),
                "max": round(self.max_value, 2),
                "avg": round(week_nutrient_value, 2),
                "avg_flag": self._get_flag_value(7 * week_nutrient_value),
                "unit": self.nutrient.unit}

    def _get_min_max(self, is_day):
        """
        Return min max for a day / or a week
        """
        if not is_day:
            return self.min_value, self.max_value
        min_value, max_value = self.min_value, self.max_value
        if self.daily_tolerance_min < 0:
            min_value = -1
        elif min_value > 0:
            min_value *= 1 - self.daily_tolerance_min
        if self.daily_tolerance_max < 0:
            max_value = -1
        elif max_value > 0:
            max_value *= 1 + self.daily_tolerance_max
        return min_value, max_value


    def get_details_with_value(self, rule, score, value, is_day=False):
        """
        Returns some details from the constraint, with a given value
        @param is_day: if True, consider to add the daily tolerance
        """
        min_value, max_value = self._get_min_max(is_day)
        res =  {"name": self.nutrient.short_name,
                "value": round(value, 2),
                "flag": self._get_flag_value(value, is_day=is_day),
                "percent_diff": 0,
                "unit": self.nutrient.unit,
                "cost": self.rule_cost(score, rule)}

        if value > 10:
            str_value = round(value)
        elif value > 1:
            str_value = round(value, 1)
        else:
            str_value = round(value, 2)

        res["str_value"] = str_value
        res["nutrient_key"] = self.nutrient.key

        if min_value > 0:
            res["min"] = round(min_value, 2)
            res["percent_min"] = min(100, round(100 * value / min_value))
            if value < min_value:
                res["percent_diff"] = 100 - res["percent_min"]
        if max_value > 0:
            res["max"] = round(max_value, 2)
            res["percent_max"] = round(100 * value / max_value)
            if value > max_value:
                res["percent_diff"] = res["percent_max"] - 100
        if min_value > 0 and max_value > 0:
            res["middle_value"] = round((res["min"] + res["max"]) / 2, 2)
        return res

    def details_per_dish(self, problem, solution, score):
        res = {}
        dish_id_to_recipes = to_dict(solution.get_recipes())

        for dish_id, recipes in dish_id_to_recipes.items():
            nutrient_value = sum(recipe.get_data_from_key(self.nutrient.key, solution.get_main_profile_recipe_ratio(dish_id)) for recipe in recipes)
            res[dish_id] = {'description': "%s %s" % (round(nutrient_value, 2), self.nutrient.unit),
                            'flag': 'neutral'}
        return res

    def get_day_cost(self, score, day_id):
        """
        Returns the cost of this constraint on one given day
        """
        for rule in self.rules:
            if type(rule) is not NutrientWeekRule and rule.day_id == day_id:
                return self.rule_cost(score, rule)
        return None

    def get_week_cost(self, score):
        for rule in self.rules:
            if type(rule) is NutrientWeekRule:
                return self.rule_cost(score, rule)
        assert False, "no cost found for week"

    def details_per_day(self, problem, solution, score):
        """
        Returns constraint details for each day.
        """
        res = {} # { day_id -> details }
        for rule in self.rules:
            if type(rule) is not NutrientWeekRule:
                day_nutrient_value = rule.get_value(solution)
                description = "%s %s" % (round(day_nutrient_value, 2), self.nutrient.unit)
                cost = self.rule_cost(score, rule)
                flag = self._get_flag_value(day_nutrient_value, is_day=True)
                res[rule.day_id] = {'description': description, 'flag': flag, 'cost': cost}
        if len(res) == 0:
            # No constraint on day. Getting nutrient values without using CPP
            dish_id_to_recipes = to_dict(solution.get_recipes())

            for day in problem.days:
                total_value = 0
                for meal_slot in day.meal_slots.all():
                    for dish in meal_slot.dishes.all():
                        recipes = dish_id_to_recipes[dish.id]
                        total_value += sum(recipe.get_data_from_key(self.nutrient.key, solution.get_main_profile_recipe_ratio(dish.id)) for recipe in recipes)
                res[day.id] = {'description': "%s %s" % (round(total_value, 2), self.nutrient.unit),
                            'flag': 'neutral', 'cost': 0}

        # Return days ordered
        return [item[1] for item in sorted(res.items(), key=lambda x: x[0])]

    def _get_flag_value(self, value, cost=None, is_day=False):
        """
        From a nutrient value, returns if it's tolerated, ok, or ko
        """
        min_value, max_value = self._get_min_max(is_day)
        if (min_value > 0 and value < min_value) or\
           (max_value > 0 and value > max_value):
            if cost is not None and cost == 0:
                return "tolerated"
            # 5% tolerance for "nearly"]
            if min_value > 0 and value < min_value and value >= min_value * 0.95:
                return "nearly"
            if max_value > 0 and value > max_value and value <= max_value * 1.05:
                return "nearly"
            return "ko"
        return "ok"


    def _get_avg_week_value(self, solution, score):
        for rule in self.rules:
            if type(rule) is NutrientWeekRule:
                return rule.get_value(solution) / rule.nb_days
        assert False, "no week constraint on a nutrient ?"

    def get_day_value(self, solution, score, day_id):
        for rule in self.rules:
            if type(rule) is NutrientDayRule and rule.day_id == day_id:
                return rule.get_value(solution)
        assert False, "cannot find day constraint (day_id = %i) ?" % day_id

    def overall_success(self, solution, score):
        """
        Returns a text that describes how the objective is reached (or not reached)
        """
        week_nutrient_value = self._get_avg_week_value(solution, score)
        return "La moyenne sur la semaine est de %s %s" % (round(week_nutrient_value, 2), self.nutrient.unit)
