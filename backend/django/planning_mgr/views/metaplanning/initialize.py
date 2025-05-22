
from rest_framework.decorators  import api_view
from rest_framework.response    import Response

from django.db                  import transaction

from common.decorators          import api_check_user_id, api_model_arg

from planning_mgr.controller.meta import reset_metaplanning

from user_mgr.models            import User

@api_view(['POST'])
@api_check_user_id
@transaction.atomic
def init_default_metaplanning(request, user_id):
    """
    If not existing, creates a default MetaPlanning for the user
    """
    meta_planning = reset_metaplanning(request.user)

    return Response({"status": "MetaPlanning initialized",
                     "planning_id": meta_planning.id}, 201)

@api_view(['POST'])
@api_model_arg("user", User)
def api_reset_metaplanning(request, user):
    """
    Remplace the user metaplanning with a brand new one
    """
    if not request.user.is_admin:
        raise PermissionDenied()
    metaplanning = reset_metaplanning(user)

    return Response({"status": "ok",
                     "metaplanning_id": metaplanning.id}, 201)
