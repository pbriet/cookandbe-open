
from common.decorators              import api_arg, api_model_arg, api_check_user_id, api_cookie_arg

from django.core.exceptions         import PermissionDenied
from django.db                          import transaction
from django.utils                   import timezone

from optalim.mongo                  import Mongo

from planning_mgr.controller.meta   import reset_metaplanning

from rest_framework.decorators      import api_view
from rest_framework.response        import Response

from recipe_mgr.models              import Ustensil

from user_mgr.controller            import UserControllerException, do_change_settings
from user_mgr.models                import User, ConfigStage, ConfigStageCompletion

@api_view(['POST'])
@api_check_user_id
@api_arg('speed', int)
@transaction.atomic
def api_preconfigure(request, user_id, speed):

    user = request.user

    # Rebuilding metaplanning with time and budget constraints
    reset_metaplanning(user, speed, user.budget)

    return Response({"status": "ok"})

@api_view(['POST'])
@api_check_user_id
@api_arg('budget', int)
@api_arg('meat', int)
@api_arg('fish', int)
def api_set_budget_proteins(request, user_id, budget, meat, fish):
    user = request.user
    user.meat_level = meat
    user.fish_level = fish
    user.budget     = budget
    user.save()
    user.meta_planning.set_modified()
    return Response({"status": "ok"})

@api_view(['GET'])
@api_check_user_id
def api_get_budget_proteins(request, user_id):
    user = request.user
    return Response({"budget": user.budget,
                     "meat": user.meat_level,
                     "fish": user.fish_level})

@api_view(['POST'])
@api_check_user_id
@api_arg("stage_key", str)
@api_arg("modify_metaplanning", bool, False)
def api_complete_config_stage(request, user_id, stage_key, modify_metaplanning):
    if modify_metaplanning and request.user.meta_planning is not None:
        # Metaplanning udpated
        request.user.meta_planning.set_modified()
    # Configuration updated
    stage = ConfigStage.objects.get(key = stage_key)
    existing_completion, created = ConfigStageCompletion.objects.get_or_create(user_id = user_id, stage_id = stage.id)
    existing_completion.date = timezone.now()
    existing_completion.save()
    return Response({"completed": "yes"})


@api_view(['put'])
def api_set_user_settings(request, user_id):
    if int(user_id) != request.user.id:
        raise PermissionDenied
    first_name = request.data.get("first_name", None)
    last_name  = request.data.get("last_name", None)
    try:
        for item in (first_name, last_name):
            if item is None or len(item) == 0:
                raise UserControllerException("Information manquante",
                    "Une erreur est survenue pendant l'envoi de vos informations, merci de réessayer plus tard")
        do_change_settings(request.user, first_name, last_name)
        response = {"status": "ok", "content" : "Vos informations ont été mises à jour"}
        status = 201
    except UserControllerException as e:
        response = {"status": "error", "title": e.title, "content": e.content}
        status = 200
    return Response(response, status)

@api_view(['post'])
@api_check_user_id
@api_model_arg('ustensil', Ustensil)
def api_user_add_ustensil(request, user_id, ustensil):
    if ustensil in request.user.ustensils.all():
        return Response({"status": "error", "content": "Ustensil already added"}, 400)
    request.user.ustensils.add(ustensil)
    return Response({"status": "ok"}, 200)

@api_view(['post'])
@api_check_user_id
@api_model_arg('ustensil', Ustensil)
def api_user_remove_ustensil(request, user_id, ustensil):
    if ustensil not in request.user.ustensils.all():
        return Response({"status": "error", "content": "No such ustensil"}, 400)
    request.user.ustensils.remove(ustensil)
    return Response({"status": "ok"}, 200)

@api_view(['POST'])
@api_model_arg("user", User)
def api_reset_configuration(request, user):
    """
    Reset the user configuration to 0%
    """
    if not request.user.is_superuser:
        raise PermissionDenied()
    for stage in ConfigStageCompletion.objects.filter(user = user):
        if not stage.expired:
            stage.delete()
    return Response({"status": "ok"}, 201)

@api_view(['POST'])
@api_arg("enabled", bool, None)
@api_arg("notifications", bool, None)
@api_arg("newsletter", bool, None)
@api_arg("daily", bool, None)
@api_arg("suggestion", bool, None)
@api_arg("why_leaving_us", str, None)
def api_set_user_email_options(request, user_id, enabled, notifications, newsletter, suggestion, daily, why_leaving_us):
    if enabled is not None:
        request.user.enabled = enabled
        if enabled is False and why_leaving_us is not None:
            mongo_table = Mongo.log_table("why_leaving_us")
            mongo_table.insert_one({"user_id": user_id, "text": why_leaving_us, "created_at": timezone.now()})
    if notifications is not None:
        request.user.mail_notifications = notifications
    if newsletter is not None:
        request.user.mail_newsletter = newsletter
    if daily is not None:
        request.user.mail_daily = daily
    if suggestion is not None:
        request.user.mail_suggestion = suggestion
    request.user.save()
    return Response({"status": "updated"}, status=201)

@api_view(['GET'])
def api_user_email_options(request, user_id):
    return Response({
        "enabled": request.user.enabled,
        "notifications": request.user.mail_notifications,
        "newsletter": request.user.mail_newsletter,
        "daily": request.user.mail_daily,
        "suggestion": request.user.mail_suggestion
        }, status=200)
