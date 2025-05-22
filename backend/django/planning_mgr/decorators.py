import datetime

from common.decorators          import api_arg

from django.core.exceptions     import PermissionDenied

from planning_mgr.models        import Dish, DishRecipe, MealSlot, Day

from rest_framework.response    import Response


def user_dishrecipe_decorator(fcn):
    """
    Decorator that retrieve a dish from a dish_id, check that this dish belongs to request.user
    and retrieve the existing dishrecipes
    """
    def new_fcn(request, dish, **kargs):
        if dish.meal_slot.day.user_id != int(request.user.id):
            return Response({"error": "dish doesn't belong to user !"}, 403)
        existing_dishrecipes = DishRecipe.objects.filter(dish_id=dish.id).order_by('order')

        return fcn(request, dish=dish, existing_dishrecipes=existing_dishrecipes, **kargs)
    return new_fcn

def ratio_decorator(fcn):
    """
    Decorator that retrieve ratio from existing dishrecipes, if it is not given by the user
    """
    def new_fcn(request, existing_dishrecipes, ratio, **kargs):
        if ratio is None:
            if existing_dishrecipes.count() == 0:
                return Response({"error": "cannot define ratio value"}, 400)
            ratio = existing_dishrecipes[0].ratio
        return fcn(request, existing_dishrecipes=existing_dishrecipes, ratio=ratio, **kargs)
    return new_fcn

def meal_slot_decorator(fcn):
    """
    Retrieves a meal slot and ensure that it belongs to the user
    """
    @api_arg('meal_slot_id', int)
    def new_fcn(request, meal_slot_id, **kargs):
        try:
            meal_slot = MealSlot.objects.select_related('day').get(pk=meal_slot_id)
        except MealSlot.DoesNotExist:
            return Response({"error": "meal slot does not exist"}, 400)
        if meal_slot.day.user_id != request.user.id:
            raise PermissionDenied
        return fcn(request, meal_slot=meal_slot, **kargs)
    return new_fcn

def day_from_date_decorator(date_arg_name):
    def decorator(fcn):
        """
        From a date given in the URL, or in GET, retrieves the day.
        """
        @api_arg(date_arg_name, datetime.date)
        def new_fcn(request, date, **kargs):
            try:
                day = Day.objects.get(date=date, user=request.user)
            except Day.DoesNotExist:
                return Response({"error": "no day existing at this date"}, 400)
            return fcn(request, day=day, **kargs)
        return new_fcn
    return decorator