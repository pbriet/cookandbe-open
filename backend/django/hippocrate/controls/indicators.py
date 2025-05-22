from collections                    import defaultdict

from common.boost                   import to_dict
from common.nutrients               import NUTRIENT_CATEGORIES

from django.utils                   import timezone

from hippocrate.models.constraints  import NutrientConstraint

from optalim.mongo                  import Mongo

from planning_mgr.models            import DishRecipe, MealSlot

import numpy


def save_indicators(problem, solution, score):
    """
    Generate and save indicators into Mongo
    """
    constraints = problem.py_constraints
    if constraints is None:
        constraints = problem.user.diet_handler.build_nutrient_constraints(problem.planning)

    values = calc_planning_indicators(constraints, solution, score)


    indicators_table = Mongo.hp_table("indicators_v2")
    # Attach the entry to a planning id
    values["planning_id"] = problem.planning.id
    values['date'] = timezone.now()
    indicators_table.update_one({'planning_id': values["planning_id"]},
                            {"$set": values}, upsert=True)


def retrieve_indicators(planning_id):
    """
    Retrieve the indicators from mongo, for a given planning
    """
    indicators_table = Mongo.hp_table("indicators_v2")
    res = indicators_table.find_one({'planning_id': planning_id})

    if res is None:
        return res

    # Removing _id which is not serializable
    del res['_id']
    return res



def calc_planning_indicators(constraints, solution, score):
    """
    Calculates a front-end ready dictionary :

    {
        'ok':
            [{
                'type': 'min_max',
                'key': ,
                'enabled': ,
                'cost':
                'daily': {
                    'min': ,
                    'max': ,
                    'values': {day_id: XXX}
                },
                'weekly': {
                    'min': ,
                    'max': ,
                    'value':
                }
            }],
        'ko':
            [{
                'type': 'simple',
                'key': ,
                'cost':

            }],
        'disabled_ok': [
            ],
        'disabled_ko'; [
        ]

    }

    """
    res = {"indicators": []}

    for constraint in constraints:

        if not constraint.is_nutrient_related():
            continue

        data = constraint.to_planning_indicator(solution, score)
        res["indicators"].append(data)


    # Calculating average duration and budget
    durations, prices = [], []
    for dishrecipes in to_dict(solution.get_dish_recipes()).values():
        for dishrecipe in dishrecipes:
            prices.append(dishrecipe.recipe.get_data_from_key("price"))

            recipe_time_vals = [dishrecipe.recipe.get_data_from_key(key) for key in ("prep_minutes", "rest_minutes", "cook_minutes")]
            durations.append(MealSlot.get_speed_from_values(*recipe_time_vals))

    res['avg_duration'] = int(round(numpy.percentile(durations, 90)))
    res['avg_price']    = int(round(numpy.percentile(prices, 90)))

    return res



def old_retrieve_indicators(problem, score):
    """
    Returns the list of constraints with their key and cost
    """
    res = {"total_cost": score.total,
           "constraints": []}

    for constraint in problem.py_constraints:
        res["constraints"].append({"key": constraint.key,
                                   "id": constraint.id,
                                   "cost": constraint.cost(score)})
    return res

