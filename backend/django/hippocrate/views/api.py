from rest_framework.decorators          import api_view
from rest_framework.response            import Response
from django.db                          import transaction
from diet_mgr.models                    import Diet
from planning_mgr.models                import DishRecipe
from planning_mgr.serializers           import PlanningMenuSerializer, DaySuggestionSerializer
from planning_mgr.controller.planning   import get_days_full_prefetch,\
                                               get_planning_including_day_full_prefetch
from hippocrate.views.serializer        import OldImprovementsSerializer
from hippocrate.models.recipestorage    import RecipeStorageNotInitialized
from hippocrate.models.problem          import Problem
from hippocrate.controls.generate       import optimize_days, improve_days, suggest_if_required
from hippocrate.controls.indicators     import old_retrieve_indicators, retrieve_indicators
from hippocrate.controls.indicators     import save_indicators
from user_mgr.models                    import User
from common.decorators                  import api_arg, api_check_user_id
from common.date                        import valid_future, today
import sys
import datetime

# Max number of planned days authorized - from today
MAX_NB_PLANNED_DAYS = 20

@api_view(['POST'])
@api_check_user_id
@api_arg('date', datetime.date, validators=[valid_future])
@api_arg('recalculate', bool, False)
@api_arg('init', bool, False)
@api_arg('reinit', bool, False)
@api_arg('restart_from_existing', bool, True)
@api_arg('auto_update_from_metaplanning', bool, True)  # If metaplanning changes, and there is no day locked after this one, automatically reset
@api_arg('minimize_change', str, None, validators=[lambda x: x in ('weak', 'strong')])
@transaction.atomic
def suggest(request, user_id, date, recalculate, init, reinit, restart_from_existing,
            minimize_change, auto_update_from_metaplanning):
    """
    Returns suggested recipes for a given date
    [{"dish_id": X, "recipe_id": Y, partial: False}, ...]

    @param recalculate: if False, will not relaunch the algorithm, unless this is a new week
    @param init: if True, will create a week if not existing
    @param reinit: if True, will recreate days from date in the week (week needs to exist)
    """
    if minimize_change is not None and not restart_from_existing:
        return Response({"error": "minimize_change can only be used with restart_from_existing"}, 400)

    if (date - today()).days > MAX_NB_PLANNED_DAYS:
        return Response({"status": "too_much_in_future", "max_nb_days": MAX_NB_PLANNED_DAYS})

    user = User.objects.select_related('meta_planning').get(pk=user_id)

    day = suggest_if_required(user, date, reinit=reinit, auto_update_from_metaplanning=auto_update_from_metaplanning,
                              init=init, recalculate=recalculate, restart_from_existing=restart_from_existing,
                              minimize_change=minimize_change)

    if day.skipped is None and day.shopping_list_id is None:
        day.skipped = False # Suggest on a given day ? Means there is a visit
        day.save()

    # Retrieving the asked day with full details
    day = get_days_full_prefetch(user, date, 1)[0]

    return Response(DaySuggestionSerializer.serialize(day, user=request.user), 200)

@api_view(['POST'])
@api_check_user_id
@api_arg('nb_days', int, 7)
@api_arg('from_date', datetime.date)
@transaction.atomic
def fill_days(request, user_id, from_date, nb_days):
    """
    Generates recipes for a given week.

    DEPRECATED: USED ONLY IN TESTS
    """
    algorithm = request.data.get("algorithm", "darwin")
    days = get_days_full_prefetch(request.user, from_date, nb_days)
    dish_ids = request.data.get("dish_ids", None)

    # Solve the problem with Hippocrate
    optimize_days(days, algorithm, dish_ids=dish_ids)

    days = get_days_full_prefetch(request.user, from_date, nb_days)
    return Response(PlanningMenuSerializer.serialize(days), 201)

@api_view(['POST'])
@api_check_user_id
@api_arg('date', datetime.date, validators=[valid_future])
def api_improve_day(request, user_id, date):
    """
    Improve a day that is within a week, by suggesting improvements on this day only
    Return the result with a suggestion format  (like "suggest" API)
    """
    days = get_planning_including_day_full_prefetch(request.user, date)
    if days is None:
        return Response({"error": "There is no valid week including day %s" % date}, 400)
    # Retrieving the day we want to improve
    day = [x for x in days if x.date == date][0]
    try:
        # Solve the problem with a max-modifs constraint
        modifications = improve_days(days, current_day=day)
    except RecipeStorageNotInitialized:
        return Response({"error": "Recipe index is not ready"}, 503)

    # Modifying the day WITHOUT SAVING IT --  warning, it requires prefetch_related to work correctly,
    # Or the serialization will reload from the database
    for meal_slot in day.ordered_meal_slots:
        ordered_dishes = []
        for dish in meal_slot.ordered_dishes:
            if dish.id in modifications:
                modif = modifications[dish.id]
                ### UGLY, but that helps a lot for genericity...
                dish.new_dishrecipe_set = list()
                for r in modif:
                    if r['ratio'] <= 0:
                        raise Exception("Invalid dishrecipe ratio : %s for dish %s" % (cpp_dishrecipe.ratio, dish_id))
                    dish.new_dishrecipe_set.append(DishRecipe(dish=dish, recipe_id=r['recipe_id'], ratio=r['ratio']))
    return Response(DaySuggestionSerializer.serialize(day, only_dishes=list(modifications.keys()), user=request.user))


@api_view(['POST'])
@api_check_user_id
@api_arg('nb_days', int, 7)
@api_arg('from_date', datetime.date)
def api_improve_days(request, user_id, from_date, nb_days):
    """
    Optimize the current week by suggesting some modifications
    """
    days = get_days_full_prefetch(request.user, from_date, nb_days)

    try:
        # Solve the problem with a max-modifs constraint
        modifications, indicators = improve_days(days, with_indicators=True)
    except RecipeStorageNotInitialized:
        return Response({"error": "Recipe index is not ready"}, 503)

    return Response({"modifications": OldImprovementsSerializer.serialize(modifications),
                     "new_indicators": indicators})


def _get_solution_score_from_week(days):
    """
    From a week, returns its current solution and the score of this solution
    """
    problem = Problem(days, init_recipe_indexes=False)
    solution = problem.build_current_solution()
    assert solution.isValid(False), "Current solution is not valid..."
    score = problem.eval(solution)
    return problem, solution, score

@api_view(['GET'])
@api_check_user_id
@api_arg('date', datetime.date)
def day_indicators(request, user_id, date):
    """
    Return day indicators, and week indicators (for day the week is included into)
    """
    day = request.user.days.get(date=date)
    indicators = retrieve_indicators(day.planning.planning.id)

    if indicators is None:
        # There are no indicators stored in Mongo
        # calculate them and store them
        days = get_planning_including_day_full_prefetch(request.user, date)
        problem, solution, score = _get_solution_score_from_week(days)
        save_indicators(problem, solution, score)
        indicators = retrieve_indicators(day.planning.planning.id)

    assert type(indicators) is dict, "Invalid type for day_indicators : %s" % indicators

    # Categorize indicators
    nutrients = {'ok': {}, 'ko': {}, 'disabled_ok': {}, 'disabled_ko': {}}

    for element in indicators["indicators"]:

        if element["key"] in ("betacarotene", "meal_balance"):
            continue # Skip betacarotene

        if 'flag' in element:
            flags = [element['flag']]
        else:
            flags = [element['weekly']['flag']]

        if 'daily' in element:
            # Retrieving data for current day only
            element['daily'] = element['daily'][str(day.id)]

            flags.append(element['daily']['flag'])

            if element['key'] == 'energiekilocalories':
                nutrients['current_day_calories'] = element['daily']['value']

        # Determine indicator flag based on week flag and day flag
        flag = get_worst_flag(flags)
        element['flag'] = flag

        category = 'ok'
        if flag == 'ko':
            category = 'ko' if element['enabled'] else 'disabled_ko'

        nutrients[category][element['key']] = element

    res = {"nutrients": nutrients,
           "avg_price": indicators['avg_price'],
           'avg_duration': indicators['avg_duration']}

    return Response({"content": res}, 200)

def get_worst_flag(flags):
    for flag in ['ko', 'nearly', 'tolerated', 'ok']:
        if flag in flags:
            return flag
    return 'ok'



@api_view(['GET'])
@api_check_user_id
@api_arg('nb_days', int, 7)
@api_arg('from_date', datetime.date)
def days_indicators(request, user_id, from_date, nb_days):
    """
    Return a list of quality indicators
    for a given week (basically, the constraints)
    and a given profile
    """
    days = get_days_full_prefetch(request.user, from_date, nb_days)
    problem, solution, score = _get_solution_score_from_week(days)

    constraints = old_retrieve_indicators(problem, score)

    return Response(constraints, 200)


@api_view(['GET'])
@api_check_user_id
@api_arg('nb_days', int, 7)
@api_arg('from_date', datetime.date)
@api_arg('constraint_id', int)
def days_indicators_details(request, user_id, from_date, nb_days, constraint_id):
    """
    On a given week, returns details about a constraint :
    per dish, per meal and/or per day  +   explanation text
    """
    days = get_days_full_prefetch(request.user, from_date, nb_days)
    problem, solution, score = _get_solution_score_from_week(days)

    constraint = problem.get_constraint(int(constraint_id))
    if constraint is None:
        return Response({"error : indicator doesn't exist"}, 400)
    return Response({
        "id": constraint.id,
        "key": constraint.key,
        "overall_success": constraint.overall_success(solution, score),
        "per_day": constraint.details_per_day(problem, solution, score),
        "per_meal": constraint.details_per_meal(solution, score),
        "per_dish": constraint.details_per_dish(problem, solution, score),
        "other_infos": constraint.other_infos(solution, score)
        }, 200)
