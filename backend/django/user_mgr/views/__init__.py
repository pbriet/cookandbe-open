from datetime                       import timedelta

from django.conf                    import settings
from django.contrib.auth            import logout
from django.core.exceptions         import PermissionDenied
from django.db                      import transaction
from django.db.models               import Q
from django.utils                   import timezone
from django.views.decorators.csrf   import ensure_csrf_cookie

import facebook

from rest_framework                 import viewsets
from rest_framework.decorators      import api_view, permission_classes
from rest_framework.permissions     import AllowAny
from rest_framework.response        import Response
from rest_framework.exceptions      import NotAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from optalim.mongo                  import Mongo

from common.date                    import parse_date_str, today
from common.decorators              import api_arg, api_model_arg, api_check_user_id, api_cookie_arg
from common.network                 import get_client_ip
from common.permissions             import Or, ReadOnly, Allow, IsStaff
from common.rest                    import CustomViewSet

from diet_mgr.models                import Diet

from emailing                       import SendmailError
from emailing.tools                 import sendmail, sendmail_template, MessageType


from planning_mgr.models            import Dish

from recipe_mgr.models              import Recipe

from user_mgr.auth                  import login, authenticate, APP_TO_USER_MODEL, update_user_subscription_level
from user_mgr.models                import User, ConfigStage, ConfigStageCompletion,\
                                           ProUser, UserOperation, Role, BaseUser, AutologinToken
from user_mgr.controller            import UserControllerException, get_reset_code, \
                                           do_signup, do_change_password, is_valid_password, \
                                           do_reset_password, do_change_login, check_email,\
                                           build_user_profile
from user_mgr.controller.promo_code import get_promotional_code_or_none
from user_mgr.controller.stats      import get_user_stats, USER_STATS_PREFETCH
from user_mgr.serializers           import ConfigStageSerializer, UserSerializer, RoleSerializer

from location_mgr.models            import Address

from paybox.views                   import NB_TRIAL_DAYS
from paybox.serializers             import SubscriptionSerializer
from paybox.models                  import Subscription

import json
import uuid

from optalim.log import logger

RESET_PASSWORD_OPERATION = "RESET_PASSWORD"

@api_view(['GET'])
@permission_classes((AllowAny, ))
@ensure_csrf_cookie
def api_init(request):
    """
    Dummy API function used to initialize the CSRF token.
    This view returns always a success, and the csrf cookie comes with it
    """
    return Response(status=200)

def log_from_facebook(request, app, oauth_access_token, create_account_if_need_be=False,
                      diet=None, diet_parameters=None, profile_metrics=None, promo_code=None):
    """
    From a Facebook access token (resulting from a facebook login on client-side),
    check the validity of the token with Facebook, and authenticate
    """
    if diet is not None or diet_parameters is not None or profile_metrics is not None:
        assert create_account_if_need_be, "Providing diet and profile parameters at login ?"
    graph = facebook.GraphAPI(version=settings.FACEBOOK_API_VERSION)
    # Verifying, with _our_ access token, if the given user access token is valid for our app
    response = graph.request('debug_token', {'access_token': settings.FACEBOOK_APP_ACCESS_TOKEN, 'input_token': oauth_access_token})
    if response['data']['is_valid']:
        user_infos = facebook.GraphAPI(oauth_access_token, version=settings.FACEBOOK_API_VERSION).get_object("me", fields="email,first_name,last_name,gender")
        if 'email' not in user_infos:
            return Response({"status": "error", "title": "Adresse email non partagée",
                                "details": "Vous devez partager votre adresse email afin de procéder à l'inscription.\n" +
                                            "- Rendez-vous sur votre page Facebook\n" +
                                            "- Cliquez sur 'Paramètres' - 'Applications'\n" +
                                            "- Supprimez 'Cook & Be'\n" +
                                            "- Rechargez cette page en appuyant sur la touche F5 et retentez l'inscription."}, 202)
        try:
            user = User.objects.get(email=user_infos['email'])
        except User.DoesNotExist:
            if not create_account_if_need_be:
                return Response({"status": "error", "title": "Aucun utilisateur ne correspond à votre email Facebook",
                                 "should_create_account": True}, 202)
            # Creating a new account
            if 'birthday' not in user_infos:
                birthday = None
                # https://developers.facebook.com/docs/apps/review/login
                # Do I Need to Submit for Login Review?
                logger.warning("No birthday in FB infos. Review process by FB may be required")
            else:
                birthday = parse_date_str(user_infos['birthday'], "%m/%d/%Y")
            user = build_user_profile(email=user_infos['email'], password=None,
                                      first_name=user_infos['first_name'],
                                      last_name=user_infos['last_name'],
                                      birth_date=birthday, sex=user_infos.get('gender', 'female'),
                                      diet=diet, diet_parameters=diet_parameters, profile_metrics=profile_metrics,
                                      promo_code=promo_code)
        if user.facebook_id != user_infos['id']:
            user.facebook_id = user_infos['id']
            user.save()
        login(request, user, app)

        refresh = RefreshToken.for_user(user)

        return Response({
            "status": "ok",
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, 200)

    # Invalid token : attempt to hijack somebody's account?
    return Response({"status": "error", "title": "Une erreur de connexion à Facebook est intervenue",
                     "details": "Veuillez réessayer plus tard"}, 202)

@api_view(['POST'])
@api_arg('fb_input_token', str)
@permission_classes((AllowAny, ))
def api_facebook_login(request, fb_input_token):
    """
    Handling login request
    """
    return log_from_facebook(request, 'public', fb_input_token)

@api_view(['POST'])
@api_arg('token', str)
@permission_classes((AllowAny, ))
def api_login_through_token(request, token):
    """
    Use the "autologin tokens" to login
    """
    try:
        uuid_token = uuid.UUID(token)
    except ValueError:
        return Response({"status": "ko", "code": "INVALID_TOKEN"})
    try:
        token_obj = AutologinToken.objects.get(token=uuid_token)
    except AutologinToken.DoesNotExist:
        return Response({"status": "ko", "code": "INVALID_TOKEN"})

    if not token_obj.is_valid():
        return Response({"status": "ko", "code": "TOKEN_EXPIRED"})

    if not token_obj.user.is_active:
        return Response({"status": "ko", "code": "DISABLED_ACCOUNT"})

    refresh = RefreshToken.for_user(token_obj.user)

    return Response({
        "status": "ok",
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, 200)


@api_view(['POST'])
@api_model_arg('user', User)
@permission_classes((Allow("admin"), ))
def api_login_as(request, user):
    """
    Login as somebody else (admin only)
    """
    login(request, user, 'public')

    refresh = RefreshToken.for_user(user)

    return Response({
        'status': 'ok',
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, 200)

@api_view(['POST'])
@permission_classes((AllowAny, ))
@api_arg('usermail', str)
@api_arg('app', str) # 'pro' or 'public'
def api_forgot_password(request, usermail, app):
    """
    Sends a reset password code
    """
    params   = json.loads(request.body.decode("utf-8"))
    user_cls = APP_TO_USER_MODEL[app]
    try:
        user = user_cls.objects.get(email = usermail)
    except user_cls.DoesNotExist:
        return Response({"status": "error", "title": "Aucun compte utilisateur n'est associé à cette adresse"})
    # Génération du code de récupération
    code     = get_reset_code()
    template_vars  = { "code": code, "email": usermail}
    try:
        sendmail_template(MessageType.REALTIME, 'user_mgr/templates/forgot_password.html', template_vars,
                          "Récupération du mot de passe", email = usermail,
                          tags=['password_recovery'], no_personal_infos=True)
    except SendmailError as e:
        return Response({"status": "error", "title": "Échec de l'envoi du message, réessayez dans quelques minutes !", "details": e.details})
    # Registering code in database
    UserOperation.objects.create(user = user, key = str(code), ip = get_client_ip(request), operation = RESET_PASSWORD_OPERATION)
    return Response({"status": "ok", "title": "Un message a été envoyé"})

@api_view(['POST'])
@permission_classes((AllowAny, ))
@api_arg('app', str) # 'pro' or 'public'
@transaction.atomic
def api_reset_password(request, app):
    """
    Handling reset password request
    """
    params   = json.loads(request.body.decode("utf-8"))
    usermail = params.get('usermail', None)
    code     = params.get('code', None)
    password = params.get('password', None)
    if request.user.is_authenticated:
        return Response({"status": "error", "title": "Vous êtes déjà authentifié"})
    try:
        tmp = UserOperation.objects.get(key=code)
        print(usermail, usermail == tmp.user.email, tmp.__dict__)
        reset = UserOperation.objects.get(user__email = usermail, key = code, operation = RESET_PASSWORD_OPERATION)
    except:
        return Response({"status": "error", "title": "Un problème est survenu pendant votre demande de changement de mot de passe. Si vous avez copié le lien dans votre navigateur, vérifiez bien que celui-ci est complet. Si le problème persiste, merci de contacter notre équipe technique."})
    if not reset.user.is_active:
        return Response({"status": "error", "title": "Ce compte utilisateur a été désactivé. Merci de contacter notre équipe technique."})
    if reset.used:
        return Response({"status": "error", "title": "Cette demande de changement de mot de passe a déjà été utilisée. Pour en effectuer une nouvelle, cliquez sur 'Annuler' puis 'Mot de passe oublié'."})
    # Todo: mettre le réglage de 1 heure de validité dans un fichier de configuration
    if timezone.now() - reset.date > timedelta(0, 60 * 60):
        return Response({"status": "error", "title": "Cette demande de changement de mot de passe a expiré. Pour en effectuer une nouvelle, cliquez sur 'Annuler' puis 'Mot de passe oublié'."})
    error_message = is_valid_password(password)
    if error_message is not None:
        return Response({"status": "error", "title": error_message})
    # All checks green, changing password and removing reset code
    do_reset_password(reset, password)
    # Finally, manual authentication
    user = authenticate(app, username = usermail, password = password)
    login(request, user, app)
    response = get_user_infos(request, _prefetch_user(user))
    response["status"] = "ok"
    return Response(response, 200)

def get_user_infos(request, user, defaultDict = None):
    if defaultDict is None:
        defaultDict = {}
    serializer = UserSerializer(user)
    res = serializer.data
    res.update(defaultDict)
    return res

def _prefetch_user(user):
    if not isinstance(user, User):
        # Pro
        return user
    return User.objects.prefetch_related('ustensils', 'user_roles').select_related('diet', 'sponsorship_code').get(pk=user.pk)

@api_view(['GET'])
@api_model_arg("user", User)
@permission_classes((Or(Allow("admin"), Allow("dietician")), ))
def api_get_user_infos(request, user):
    return Response(get_user_infos(request, _prefetch_user(user)), 200)

@api_view(['GET'])
@permission_classes((AllowAny, ))
def api_current_user(request):
    """
    Return which is the current user logged in on this session
    """
    if not request.user.is_authenticated:
        response = {"status": "not logged in"}
    else:
        # Quite ugly : this is where we check if the subscription is expired or not.
        # Because this function is called either :
        # - after login
        # - at session initialization (if already logged in)
        expired = update_user_subscription_level(request.user)
        response = get_user_infos(request, _prefetch_user(request.user), {"status": "logged in", 'just_expired': expired})
    return Response(response, 200)

@api_view(['put'])
def api_set_user_login(request, user_id):
    if int(user_id) != request.user.id:
        raise PermissionDenied
    login  = request.data.get('email', None)
    if login is None or len(login) == 0:
        return Response({"status" : "error", "title" : "Nouvelle adresse email incorrecte"}, 200)
    try:
        do_change_login(request.user, login)
        response = {"status": "ok", "content" : "Un email vous a été envoyé pour valider le changement d'adresse"}
        status = 201
    except UserControllerException as e:
        response = {"status": "error", "title": e.title, "content": e.content}
        status = 200
    return Response(response, status)

@api_view(['put'])
def api_set_user_password(request, user_id):
    if int(user_id) != request.user.id:
        raise PermissionDenied
    try:
        do_change_password(request.user, request.data)
        response = {"status": "ok", "content" : "Votre mot de passe a été mis à jour"}
        status = 201
    except UserControllerException as e:
        response = {"status": "error",
                    "title": "Changement de mot de passe impossible",
                    "content": e.content}
        status = 200
    return Response(response, status)

@api_view(['post'])
@api_model_arg('role', Role)
@api_model_arg('user', User)
@permission_classes((Allow("admin"), ))
def secure_user_add_role(request, user, role):
    if user.user_roles.filter(role = role).count() > 0:
        return Response({"status": "error", "content": "Role already added"}, 400)
    user.user_roles.create(role = role, created_by = request.user)
    return Response({"status": "ok"}, 200)

@api_view(['post'])
@api_model_arg('role', Role)
@api_model_arg('user', User)
@permission_classes((Allow("admin"), ))
def secure_user_remove_role(request, user, role):
    if user.user_roles.filter(role = role).count() == 0:
        return Response({"status": "error", "content": "No such role"}, 400)
    user.user_roles.filter(role = role).delete()
    return Response({"status": "ok"}, 200)

@api_view(['POST'])
@permission_classes((AllowAny, ))
@api_arg('email', str, None)
@api_arg('password', str, None)
@api_arg('first_name', str, None)
@api_model_arg('pro', ProUser, allow_none=True)
@api_model_arg('diet', Diet, allow_none=True, id_arg_name="diet_key", pk_name="key", pk_type=str)
@api_arg('diet_parameters', dict, None)
@api_arg('profile_metrics', dict, None)
@api_arg('app', str)
@api_arg('promo_code', str, None)
@api_cookie_arg('op_uuid', allow_none=True)
def api_signup(request, email, password, first_name, diet, pro, diet_parameters,
               profile_metrics, app, op_uuid, promo_code):
    """
    Handling query of sign up
    """
    try:
        with transaction.atomic():
            user = do_signup(email, password, first_name, diet=diet, diet_parameters=diet_parameters,
                             profile_metrics=profile_metrics, promo_code=promo_code)
        if pro is not None:
            user.pro = pro
            user.save()
        login(request, user, app)

        refresh = RefreshToken.for_user(user)

        response = {
            "status": "ok",
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

        status = 201
    except UserControllerException as e:
        response = {"status": "error",
                    "title": e.title,
                    "details": e.content}
        status = 200
    return Response(response, status)

@api_view(['GET'])
@permission_classes((AllowAny, ))
@api_arg('value', str)
def api_check_promo_code(request, value):
    promo_code = get_promotional_code_or_none(value)
    if promo_code is None:
        return Response({'is_valid': False, 'error': "Ce code n'existe pas ou n'est plus valide"})
    return Response({'is_valid': True})

@api_view(['POST'])
@permission_classes((AllowAny, ))
@api_arg('access_token', str)
@api_arg('app', str)
@api_model_arg('diet', Diet, allow_none=True, id_arg_name="diet_key", pk_name="key", pk_type=str)
@api_arg('diet_parameters', dict, None)
@api_arg('profile_metrics', dict, None)
@api_arg('promo_code', str, None)
@api_cookie_arg('op_uuid', allow_none=True)
def api_facebook_signup(request, access_token, diet, diet_parameters, profile_metrics, app, op_uuid, promo_code):
    """
    Login or create account from Facebook
    """
    try :
        with transaction.atomic():
            response = log_from_facebook(request, app, access_token, create_account_if_need_be=True,
                                        diet=diet, diet_parameters=diet_parameters, profile_metrics=profile_metrics,
                                        promo_code=promo_code)
        return response
    except UserControllerException as e:
        data = {"status": "error",
                "title": e.title,
                "details": e.content}
        return Response(data, 200)

@api_view(['GET'])
@api_arg('user_id', int)
def api_user_stats(request, user_id):
    """
    Returns some interesting infos about one user
    """
    user = User.objects.prefetch_related(*USER_STATS_PREFETCH).get(pk = user_id)
    if not request.user.is_authenticated:
        raise NotAuthenticated
    if not request.user.is_admin and not request.user.is_dietician and user.id != request.user.id:
        raise PermissionDenied
    res = get_user_stats(user)
    return Response(res)

@api_view(['GET'])
@api_arg('max_count', int, 10)
def api_user_search(request, keyword, max_count):
    query = User.objects.all()
    if keyword:
        condition = Q(email__icontains = keyword) | Q(first_name__icontains = keyword) | Q(last_name__icontains = keyword)
        if keyword.isdigit():
            condition = condition | Q(pk = int(keyword))
        query = query.filter(condition)
    query = query.order_by('last_name', 'first_name').prefetch_related('ustensils', 'user_roles')
    query.select_related('diet', 'sponsorship_code')
    if max_count:
        query = query[:max_count]
    serializer = UserSerializer(query, many = True)
    # Stats
    count = query.count()
    # Return
    return Response({"results": serializer.data, "count" : count, "keyword" : keyword}, 200)

@api_view(['GET'])
@api_check_user_id
def api_config_stages_status(request, user_id):
    """
    Returns :
    * What is the profile completion
    * What is the next stage to complete
    """
    stage_completions = {} # stage_id => StageCompletion
    for csc in ConfigStageCompletion.objects.filter(user=request.user):
        stage_completions[csc.stage_id] = csc
    all_stages = list(ConfigStage.objects.all().order_by('order'))

    nb_completed_stages = 0
    next_stage = None

    for stage in all_stages:
        if stage.id in stage_completions and not stage_completions[stage.id].expired:
            nb_completed_stages += 1
            continue
        if next_stage is None:
            next_stage = stage

    if next_stage is None:
        next_stage_serialized = None
    else:
        next_stage_serialized = ConfigStageSerializer(next_stage).data
        if next_stage.id in stage_completions:
            next_stage_serialized["status"] = "expired"
        else:
            next_stage_serialized["status"] = "empty"

    return Response({"nb_stages": len(all_stages),
                     "nb_completed": nb_completed_stages,
                     "completion": round(100 * float(nb_completed_stages) / len(all_stages)),
                     "next_stage": next_stage_serialized})

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (Or(ReadOnly("admin", list = True)), )

class ConfigStageViewSet(CustomViewSet):
    model = ConfigStage
    serializer_class = ConfigStageSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('order')

    def list(self, request, *args, **kwargs):
        objs = list(self.get_queryset())
        serialized = ConfigStageSerializer(objs, many = True).data

        user_id = self.request.query_params.get('user_id')
        if user_id is not None:
            user_id = int(user_id)
            if user_id != self.request.user.id:
                raise PermissionDenied
            self._add_user_infos(serialized)

        return Response(serialized, 200)

    def _add_user_infos(self, serialized):
        """
        For each stage, adds the completion status for the current user
        """
        stage_completions = {} # stage id => completion
        for completion in ConfigStageCompletion.objects.filter(user=self.request.user):
            stage_completions[completion.stage_id] = completion

        for elt in serialized:
            if elt['id'] not in stage_completions:
                elt['status'] = 'empty'
            elif stage_completions[elt['id']].expired:
                elt['status'] = 'expired'
            else:
                elt['status'] = 'filled'

@api_view(['POST'])
@api_model_arg("user", User)
def api_delete_user(request, user):
    """
    Remove a user and all its related objects
    """
    if not request.user.is_superuser:
        raise PermissionDenied()
    nb_recipes = user.written_recipes.filter(status__gte=Recipe.STATUS_PUBLISHED).count()
    if nb_recipes > 0:
        return Response({"status": "error", "details": "cannot delete user, because he/she has some published recipes attached (%i)" % nb_recipes}, 200)
    user.delete()
    return Response({"status": "ok"}, 201)

@api_view(['POST'])
@api_model_arg("user", User)
@api_arg("nb_subscriptions", int, 12)
@permission_classes((Allow("admin"), ))
def api_user_last_subscriptions(request, user, nb_subscriptions):
    if not request.user.is_superuser:
        raise PermissionDenied()
    subscriptions = Subscription.objects.filter(user = user).order_by("-id")[0:nb_subscriptions]
    return Response({"active": user.current_subscription_id, "results": [SubscriptionSerializer(s).data for s in subscriptions]}, 200)

@api_view(['GET'])
@api_model_arg("user", User)
def api_user_question_quota(request, user):
    if not request.user.is_authenticated or (user.id != request.user.id and not request.user.is_admin):
        raise PermissionDenied
    return Response(user.question_quota.serialize(), status = 200)

@api_view(['POST'])
@api_arg("postal_code", str)
@api_model_arg("user", User)
def api_set_user_postal_code(request, user, postal_code):
    if not request.user.is_authenticated or (user.id != request.user.id and not request.user.is_admin):
        raise PermissionDenied
    if user.main_address is None:
        user.main_address = Address.objects.create(postal_code = postal_code)
        user.save()
    else:
        user.main_address.postal_code = postal_code
        user.main_address.save()
    return Response({"status": "updated"}, status=201)

@api_view(['GET'])
@permission_classes((Allow("admin"), ))
def api_why_leaving_results(request):
    table = Mongo.log_table("why_leaving_us")
    cursor = table.find({}, {'_id': False}).sort("created_at", -1)
    return Response({"data": sorted(list(cursor), key=lambda x: x["created_at"], reverse=True)})
