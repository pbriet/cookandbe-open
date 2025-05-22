
from rest_framework.decorators  import api_view
from rest_framework.response    import Response
from common.decorators          import api_check_user_id, api_arg

@api_view(['POST'])
@api_check_user_id
@api_arg('meal_type_id', int)
@api_arg('value', int)
def set_meal_speed(request, user_id, value, meal_type_id):
    """
    Modifies the structure of one dish within a meal  (forced recipe, recipe tags, food tags)
    """
    meta_planning = request.user.meta_planning

    for day in meta_planning.days.all():
        for meal_slot in day.meal_slots.prefetch_related("dishes__dish_type").filter(meal_type_id=meal_type_id):
            meal_slot.speed = value
            meal_slot.save()

    meta_planning.set_modified()
    return Response({"status": "updated"})