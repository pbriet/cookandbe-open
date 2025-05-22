from rest_framework.decorators  import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.response    import Response
from rest_framework             import viewsets

from django.db                  import transaction
from django.core.exceptions     import PermissionDenied

from common.decorators          import api_check_user_id, api_model_arg, api_arg
from common.permissions         import Or, ReadWrite, ReadOnly

from diet_mgr.controller        import assign_diet
from diet_mgr.handlers          import InvalidDietParametersException
from diet_mgr.models            import UserDietParameter, Diet
from diet_mgr.serializers       import DietSerializer

from recipe_mgr.models          import FoodTag
from recipe_mgr.serializers     import FoodTagSerializer


@api_view(['POST'])
@api_check_user_id
@api_model_arg('diet', Diet)
@api_arg('parameters', dict, {})
@transaction.atomic
def subscribe_to_diet(request, user_id, diet, parameters):
    """
    Makes the user subscribe to a diet
    @param parameters: The diet parameters : {name: value}
    """
    if diet.enabled is False and not request.user.is_admin and not request.user.is_operator:
        raise PermissionDenied
    try:
        assign_diet(request.user, diet, parameters)
    except InvalidDietParametersException as exc:
        return Response({'status': 'error', "error": str(exc)}, 400)
    res = {"status": "success"}
    if request.user.diet_id is not None and request.user.activated_diet.id != request.user.diet_id:
        res["requires_subscription"] = True
    return Response({"status": "success"}, 201)

@api_view(['GET'])
@api_check_user_id
def current_diet_parameters(request, user_id):
    """
    Returns a dictionnary of current diet parameters
    """
    diet_handler = request.user.diet_handler
    return Response(diet_handler.load_parameters(), 200)

@api_view(['POST'])
@api_check_user_id
@api_model_arg('diet', Diet)
@api_arg('arguments', dict, {})
@api_arg('auto_select', bool, False)
@transaction.atomic
def diet_diagnose(request, user_id, diet, arguments, auto_select):
    """
    From the arguments, returns a diagnosis
    """
    try:
        res = diet.handler(request.user.main_profile).diagnose(arguments)
        if auto_select:
            assign_diet(request.user, diet, res['params'])
    except InvalidDietParametersException as exc:
        return Response({'status': 'error', "error": str(exc)}, 200)

    return Response({'status': 'ok', 'content': res}, 200)

@api_view(['GET'])
@api_model_arg('diet', Diet)
def diet_excluded_foodtags(request, diet):
    return Response(FoodTagSerializer(diet.excluded_food_tags.all(), many=True).data)

@api_view(['GET'])
@api_model_arg('diet', Diet)
def diet_forewarned_foodtags(request, diet):
    return Response(FoodTagSerializer(diet.forewarned_food_tags.all(), many=True).data)

@api_view(['GET'])
@api_model_arg('diet', Diet, allow_none=True, id_arg_name="diet_key", pk_name="key", pk_type=str)
def diet_from_key(request, diet):
    return  Response(DietSerializer(diet).data, 200)

@api_view(['GET'])
@permission_classes((AllowAny, ))
@api_arg('url_key', str)
def diet_from_url_key(request, url_key):
    try:
        diet = Diet.objects.get(url_key=url_key)
    except Diet.DoesNotExist:
        return Response({"error": "no such diet"}, 400)
    return  Response(DietSerializer(diet).data, 200)

class DietViewSet(viewsets.ModelViewSet):
    queryset = Diet.objects.order_by('min_subscription_level', "id") # The free ones first
    serializer_class = DietSerializer

    permission_classes = ( Or(ReadWrite("operator", list = True), ReadOnly(list = True)), )

    def list(self, request):
        queryset = self.get_queryset()
        # Only operators can access disabled diets
        if not request.user.is_authenticated or (not request.user.is_operator and not request.user.is_admin):
            queryset = queryset.filter(enabled = True)
        queryset = queryset.order_by('rank')
        return Response(DietSerializer(queryset, many = True).data, 200)

    @action(detail=True, methods=['post'])
    @api_model_arg('food_tag', FoodTag)
    def exclude_foodtag(self, request, pk, food_tag):
        diet = self.get_object()
        if diet.excluded_food_tags.filter(pk=food_tag.id).count():
            return Response({"error": "is already excluded"}, 400)
        diet.excluded_food_tags.add(food_tag)
        return Response({"status": "done"}, 201)

    @action(detail=True, methods=['post'])
    @api_model_arg('food_tag', FoodTag)
    def undo_exclude_foodtag(self, request, pk, food_tag):
        diet = self.get_object()
        if not diet.excluded_food_tags.filter(pk=food_tag.id).count():
            return Response({"error": "is not excluded"}, 400)
        diet.excluded_food_tags.remove(food_tag)
        return Response({"status": "done"}, 201)
