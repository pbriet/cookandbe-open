
from common.boost                   import to_dict

from optalim.config                 import Config
from optalim.main                   import OptalimWebsite

from hippocrate.controls.indicators import save_indicators, old_retrieve_indicators
from hippocrate.controls.logs       import save_darwin_finished_logs, save_constraint_logs, save_darwin_started_log
from hippocrate.models.problem      import Problem

from planning_mgr.controller.meta   import check_can_auto_update_from_meta
from planning_mgr.controller.planning   import get_planning_including_day_full_prefetch, build_planning

import time
from optalim.log import logger

def _preload_config():
    # Reload darwin config on the fly
    OptalimWebsite.load_darwin_config()
    # Reload ANC config on the fly
    Config.load_anc()


def suggest_if_required(user, date, reinit=False, auto_update_from_metaplanning=True,
                        init=True, recalculate=False, restart_from_existing=True,
                        minimize_change=None):
    """
    For a given user, on a given date, generates 7 days - ONLY IF REQUIRED
    @param init: if there is no day, initialize one  (otherwise returns None)
    @param reinit: force regeneration of planning from metaplanning
    @param recalculate: force recalculation of dishes, without rebuilding from metaplanning
    @param auto_update_from_metaplanning: If metaplanning changes, and there is no day locked after this one, automatically reset
    @param restart_from_existing: start optimization with the existing dishrecipes
    @param minimize_change: Minimize the number of modifications from existing planning
    @return the day generated (or preexisting)
    """
    day = user.days.filter(date=date)
    if len(day) == 0:
        day = None
    else:
        day = day[0]

    if day is not None and not reinit and auto_update_from_metaplanning:
        if check_can_auto_update_from_meta(user, day):
            reinit = True

    if day is None or (not day.is_skipped() and day.shopping_list_id is None and (reinit or recalculate)):
        day = try_to_optimize(user, date, recalculate, init, reinit, restart_from_existing,
                              minimize_change, auto_update_from_metaplanning)

    return day


def try_to_optimize(user, date, recalculate, init, reinit, restart_from_existing,
                    minimize_change, auto_update_from_metaplanning):
    """
    Try to optimize one day
    """
    new_week = False
    # Get the planning days containing date (returns None if not such planning)
    days = get_planning_including_day_full_prefetch(user, date)

    if reinit:
        if days is None:
            # Reinit with no existing planning -> like a init
            init = True
        else:
            # Create a new week starting on date
            new_week = True

    if init and days is None:
        # Initialization. If there is no planning existing, build a new one
        new_week = True

    if new_week:
        # Clear the existing days (if so) older than "date", a adds 7 days starting on "date"
        build_planning(user, date, 7, clear_existing=True)
        # Reloading the days
        days = get_planning_including_day_full_prefetch(user, date)

    current_day = [day for day in days if day.date == date][0]

    if reinit or new_week or recalculate:
        # We need to run the engine to fill the empty days
        optimize_days(days, "darwin",
                      start_from_existing_solution=(restart_from_existing and not reinit and not init),
                      minimize_change=minimize_change, current_day=current_day)

    return current_day


def optimize_days(days, algorithm='darwin', **kargs):
    """
    Re-generate some days with a given algorithm.
    @param dish_ids: If not None, only these dish_ids can change
                   (note: others can change, but only quantities)
    """
    _preload_config()

    problem = Problem(days, **kargs)

    save_darwin_started_log(problem)

    t = time.time()
    solution = getattr(problem, "solve_" + algorithm)()
    logger.info("Solution solved in %ss" % round(time.time() - t, 2))

    # Clean the previous solution stored
    problem.clean_previous_solution()

    # Save the result in the DB
    problem.save_solution(solution)

    score = problem.eval(solution)

    # Generate indicators and save them in Mongo
    save_indicators(problem, solution, score)

    # Save how much time it took
    save_darwin_finished_logs(problem)
    save_constraint_logs(problem, solution, score)

    # Contains all settings used
    return problem, solution

def improve_days(days, current_day=None, with_indicators=False):
    """
    Executes the optimization algorithm with a constraint on number of modifications
    @param current_day: Day object
    """
    _preload_config()

    problem = Problem(days, minimize_change='strong', start_from_existing_solution=True,
                      make_validated_mutable=True,    current_day=current_day)

    solution1 = problem.build_current_solution()

    save_darwin_started_log(problem)

    t = time.time()
    solution2 = problem.solve_darwin()
    logger.info("Improved in %ss" % round(time.time() - t, 2))

    # Save how much time it took
    save_darwin_finished_logs(problem)

    # Extracting the modifications from the new solution
    modifications = {}

    recipe_dict1 = to_dict(solution1.get_recipes())
    recipe_dict2 = to_dict(solution2.get_recipes())

    for dish_id in problem.dish_index.all_dish_ids:
        recipe_ids1 = sorted([r.recipe_id for r in recipe_dict1[dish_id]])
        recipe_ids2 = sorted([r.recipe_id for r in recipe_dict2[dish_id]])

        if recipe_ids1 != recipe_ids2:
            modifications[dish_id] = []
            for r_id in recipe_ids2:
                ratio = solution2.get_total_recipe_ratio(dish_id)
                if ratio < 0.1:
                    raise Exception("Invalid dishrecipe ratio : %s for dish %s" % (ratio, dish_id))
                modifications[dish_id].append({'recipe_id': r_id,
                                               'ratio': ratio})

    if not with_indicators:
        return modifications

    # Retrieving the indicators for the new solution
    score = problem.eval(solution2)
    indicators = old_retrieve_indicators(problem, score)

    return modifications, indicators

