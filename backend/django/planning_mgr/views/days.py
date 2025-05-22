
from rest_framework.decorators          import api_view
from rest_framework.response            import Response
from common.decorators                  import api_arg, api_check_user_id
from planning_mgr.models                import Day
from planning_mgr.controller.planning   import build_planning, clear_days
from planning_mgr.serializers           import PlanningMenuSerializer

import datetime

@api_view(['POST'])
@api_check_user_id
@api_arg('nb_days', int, 7)
@api_arg('from_date', datetime.date)
def add_days(request, user_id, from_date, nb_days):
    """
    Creates N days, starting from_date
    """
    if request.user.meta_planning is None:
        return Response({"error": "user has no metaplanning"}, 400)

    nb_days_existing = Day.objects.filter(date__gte=from_date, user_id=user_id).count()
    if nb_days_existing > 0:
        return Response({"error": "days already exist after %s" % from_date}, 400)

    days = build_planning(request.user, from_date, nb_days)

    return Response(PlanningMenuSerializer.serialize(days), 201)

@api_view(['POST'])
@api_check_user_id
@api_arg('nb_days', int, 7)
@api_arg('from_date', datetime.date)
def clear_days_api(request, user_id, from_date, nb_days):
    """
    Remove all existing days after from_date
    """
    if request.user.meta_planning is None:
        return Response({"error": "user has no metaplanning"}, 400)
    if from_date <= datetime.date.today():
        return Response({"error": "you cannot delete past days (including today"}, 400)
    clear_days(request.user, from_date)

    return Response({"status": "ok"})