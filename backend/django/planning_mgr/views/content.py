from rest_framework.decorators  import api_view
from rest_framework.response    import Response

from django.core.exceptions     import PermissionDenied

from common.date                import today
from common.decorators          import api_arg, api_check_user_id

from planning_mgr.models        import Day, MealType
from planning_mgr.serializers   import PlanningMenuSerializer, MealSlotLightSerializer,\
                                       DayToFillSerializer, MealSlotFullSerializer

from planning_mgr.controller.planning    import get_days_full_prefetch, get_last_planning_days
from planning_mgr.controller.meal        import get_next_meal_full_prefetch
from recipe_mgr.helpers         import detect_aggregations
from recipe_mgr.models          import DishType

import datetime

@api_view(['GET'])
@api_check_user_id
@api_arg('date', datetime.date)
def day_content_view(request, user_id, date):
    """
    Returns the meals of a given day
    """
    try:
        day = Day.objects.prefetch_related('meal_slots__dishes__dishrecipe_set', 'meal_slots__dishes__dish_type')\
                         .get(user_id = user_id, date = date)
    except Day.DoesNotExist:
        return Response({"status": "this day is not generated"}, status=200)

    res = []
    for meal_slot in day.ordered_meal_slots:
        res.append(MealSlotLightSerializer.serialize(meal_slot))

    return Response({"status": "success",
                     "date": str(date),
                     "content": res}, status=200)

@api_view(['GET'])
@api_check_user_id
@api_arg('nb_days', int, 7)
@api_arg('from_date', datetime.date)
@api_arg('allow_empty_days', bool, False)
@api_arg('show_static', bool, False)
def get_menu(request, user_id, from_date, nb_days, allow_empty_days, show_static):
    days = get_days_full_prefetch(request.user, from_date, nb_days, allow_empty_days=allow_empty_days)
    res = {"ready": True, "content": PlanningMenuSerializer.serialize(days, show_static)}
    return Response(res, 200)

@api_view(['GET'])
@api_check_user_id
@api_arg('offset', datetime.datetime, None)
def get_next_meal(request, user_id, offset):
    meal = get_next_meal_full_prefetch(request.user, offset)
    if meal is None:
        return Response({'status' : 'No meal planned'}, 200)
    return Response(MealSlotFullSerializer.serialize(meal), 200)

@api_view(['GET'])
@api_check_user_id
@api_arg('date', datetime.date)
def day_to_fill(request, user_id, date):
    """
    Returns a serialized version of a day, with the partial completion of recipes
    """
    day = get_days_full_prefetch(request.user, date, 1)[0]
    res = DayToFillSerializer.serialize(day)
    return Response(res, 200)

@api_view(['GET'])
@api_check_user_id
@api_arg('dates', datetime.date, is_list=True)
def days_states(request, user_id, dates):
    """
    Returns for each day its status : 'empty', 'skipped', 'validated'
    """
    days = request.user.days.filter(date__in=dates)
    day_by_date = dict((d.date, d) for d in days)
    
    res = []
    values = {None: 'empty', False: 'validated', True: 'skipped'}
    for d in dates:
        day = day_by_date.get(d)
        if d <= today():
            res.append('past')
        elif day is not None and day.shopping_list_id:
            res.append('locked')
        else:
            skipped = None
            if day is not None:
                skipped = day.skipped
            res.append(values[skipped])
    return Response({"states": res}, 200)


@api_view(['GET'])
@api_check_user_id
def days_last_block(request, user_id):
    """
    Returns :
    - if there is at least 7 continuous days in the DB, what is the last block of 7 days
    """
    week_days = get_last_planning_days(request.user)
    if week_days is None:
        return Response({"status": "no week block detected"}, 200)

    return Response({'last_days_block': {'first_day': week_days[0].date,
                                         'last_day': week_days[-1].date}
                                         }, 200)

@api_view(['GET'])
@api_check_user_id
def api_planification_status(request, user_id):
    """
    Returns current status of planification and shopping
    """
    days = list(request.user.days.filter(date__gte=today(), skipped__isnull=False).order_by('-date'))
                
    res = {
        "planned_to": None,
        "suggested_to": None,
        "days_not_in_list": False
    }
    if len(days) > 0:
        res["planned_to"] = days[0].date
        suggested_days = list(d for d in days if d.skipped == False)
        if len(suggested_days) > 0:
            res["suggested_to"] = suggested_days[0].date
            res["days_not_in_list"] = any(d.shopping_list_id is None for d in suggested_days)
    return Response(res, 200)

@api_view(['GET'])
@api_arg('meal_type_id', int)
def meal_type_dish_types(request, meal_type_id):
    """
    Returns the possible dish types for a given meal type
    """
    try:
        meal_type = MealType.objects.prefetch_related('dish_types').get(pk=meal_type_id)
    except MealType.DoesNotExist:
        return Response({"error": "Meal type doesn't exist"}, 400)

    dish_types = meal_type.dish_types.all()
    dish_type_ids = sorted([dt.id for dt in dish_types])
    agg_dish_type_ids = detect_aggregations(dish_type_ids).keys()
    
    agg_dish_types = DishType.objects.filter(id__in=agg_dish_type_ids)
    assert len(agg_dish_types) == len(agg_dish_type_ids)
    dish_types = sorted(list(dish_types) + list(agg_dish_types), key=lambda x: x.id)

    res = []
    for dish_type in dish_types:
        res.append({"id":   dish_type.id,
                    "name": dish_type.name})

    return Response({'dish_types': sorted(res, key=lambda x: x['id'])}, 200)