from rest_framework.response    import Response
from django.core.exceptions     import PermissionDenied
from eater_mgr.models           import Eater


def eater_decorator(fcn):
    """
    Retrieves a meal slot and ensure that it belongs to the user
    """
    def new_fcn(request, eater_id, **kargs):
        try:
            eater = Eater.objects.get(pk=eater_id)
        except Eater.DoesNotExist:
            return Response({"error": "eater does not exist"}, 400)
        if eater.user_id != request.user.id:
            raise PermissionDenied
        return fcn(request, eater=eater, **kargs)
    return new_fcn
