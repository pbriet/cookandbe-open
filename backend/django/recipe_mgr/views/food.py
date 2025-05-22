from collections                import defaultdict

from rest_framework             import viewsets
from rest_framework.decorators  import api_view, action
from rest_framework.response    import Response

from common.decorators          import api_arg
from common.model               import get_field_validators
from common.permissions         import IsAdminOrReadOnly

from recipe_mgr.models          import Food, FoodType, FoodSeasonality
from recipe_mgr.serializers     import FoodSerializer, CookingMethodSerializer, RawStateSerializer, FoodTypeSerializer

FOOD_SEARCH_SHOW_CATEGORIES_OVER = 30

class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = (IsAdminOrReadOnly, )

    @action(detail=True, methods=['get'])
    def available_options(self, request, pk):
        raw_states = self.get_object().available_raw_states()
        cooking_methods = self.get_object().available_cooking_methods()
        return Response({"cooking_methods": CookingMethodSerializer(cooking_methods, many=True).data,
                         "raw_states": RawStateSerializer(raw_states, many=True).data})

    @action(detail=True, methods=['get'])
    def available_raw_states(self, request, pk):
        """
        Returns raw states that are available for this food (through FoodNutrient)
        """
        raw_states = self.get_object().available_raw_states()
        return Response(RawStateSerializer(raw_states, many=True).data)

    @action(detail=True, methods=['get'])
    def available_cooking_methods(self, request, pk):
        """
        Returns cooking methods that are available for this food (through FoodNutrient)
        """
        cooking_methods = self.get_object().available_cooking_methods()
        return Response(CookingMethodSerializer(cooking_methods, many=True).data)

    @action(detail=True, methods=['post'])
    @api_arg('name', str)
    def set_name(self, request, pk, name):
        """
        Add one dish type to a recipe
        """
        food = self.get_object()
        food.name = name
        food.save()
        return Response({}, 201)

    @action(detail=True, methods=['post'])
    @api_arg('enabled', bool)
    def set_enabled(self, request, pk, enabled):
        food = self.get_object()
        food.enabled = enabled
        food.save()
        return Response({}, 201)

    @action(detail=True, methods=['get'])
    def seasonality(self, request, pk):
        food = self.get_object()
        try:
            season = FoodSeasonality.objects.get(food=food)
        except FoodSeasonality.DoesNotExist:
            return Response({"status": "no_season"})
        return Response({"status": "season", "start_month": season.start_month,
                         "end_month": season.end_month})

    @action(detail=True, methods=['post'])
    @api_arg('start_month', int, validators=get_field_validators(FoodSeasonality, 'start_month'))
    @api_arg('end_month',   int, validators=get_field_validators(FoodSeasonality, 'end_month'))
    def set_seasonality(self, request, pk, start_month, end_month):
        food = self.get_object()
        if start_month == 1 and end_month == 12:
            # Ok, there's no season really
            FoodSeasonality.objects.filter(food=food).delete()
            return Response({"status": "ok"})
        # Replace with update_or_create (Django 1.7)
        season = FoodSeasonality.objects.get_or_create(food=food, defaults={'start_month': start_month, 'end_month': end_month})
        if not season[1]:
            # Already existing : needs update
            season[0].start_month = start_month
            season[0].end_month = end_month
            season[0].save()
        return Response({"status": "ok"})

    @action(detail=True, methods=['post'])
    @api_arg('conversion', int, None)
    @api_arg('raw_state', int, None)
    @api_arg('cooking_method', int, None)
    def set_defaults(self, request, pk, conversion, raw_state, cooking_method):
        """
        Add one dish type to a recipe
        """
        food = self.get_object()
        food.default_conversion_id      = conversion
        food.default_raw_state_id       = raw_state
        food.default_cooking_method_id  = cooking_method
        food.save()
        return Response({}, 201)

@api_view(['GET'])
@api_arg('return_categories', bool, False)
@api_arg('with_season', bool, False)
@api_arg('disabled_only', bool, False)
@api_arg('show_disabled', bool, True)
@api_arg('offset', int, 0)
@api_arg('keyword', str, None)
@api_arg('type_id', int, None)
@api_arg('limit', int, FOOD_SEARCH_SHOW_CATEGORIES_OVER)
@api_arg('offset', int, 0)
def food_search(request, keyword, return_categories, with_season, type_id, disabled_only, show_disabled, limit, offset):
    if limit > FOOD_SEARCH_SHOW_CATEGORIES_OVER and not request.user.is_operator:
        limit = FOOD_SEARCH_SHOW_CATEGORIES_OVER
    base_query = Food.objects.select_related('type')
    if not request.user.is_operator:
        base_query = base_query.filter(enabled = True)
    else:
        if disabled_only:
            base_query = base_query.filter(enabled = False)
        elif not show_disabled:
            base_query = base_query.filter(enabled = True)
    if type_id is not None:
        type_id = int(type_id)
        base_query = base_query.filter(type__id=type_id)
    else:
        if keyword is None:
            return Response({"error": "no keyword"}, 400)

    if keyword is not None and len(keyword) > 0:
        for word in keyword.split(' '):
            if len(word) > 0:
                base_query = base_query.filter(name__unaccent__icontains = word)

    nb_foods = base_query.count()
    foods = list(base_query.extra(select={'length':'Length("recipe_mgr_food"."name")'}).order_by('length'))
    empty = (nb_foods == 0)

    nb_per_types = defaultdict(int)
    for food in foods:
        if type_id is None or food.type_id == food.type_id:
            nb_per_types[food.type] += 1

    # Sorting food types per number of food -- descending, and serializing
    serialized_types = []
    if return_categories or (nb_foods > FOOD_SEARCH_SHOW_CATEGORIES_OVER and type_id is None):
        for food_type, nb in sorted(nb_per_types.items(), key=lambda x:x[1], reverse=True):
            serialized_types.append({"type": FoodTypeSerializer(food_type).data, "nb_food": nb})

    serializer = FoodSerializer(foods[offset:offset+limit], with_season=with_season, many=True)

    res = {
        "foods": serializer.data,
        "types": serialized_types,
        "empty": empty,
        "keywords": keyword,
        "count": nb_foods,
        }
    return Response(res)

class FoodTypeViewSet(viewsets.ModelViewSet):
    serializer_class = FoodTypeSerializer
    permission_classes = (IsAdminOrReadOnly, )

    def get_queryset(self):
        filter_empty = bool(self.request.query_params.get('filter_empty', True))
        queryset = FoodType.objects.all()
        if filter_empty:
            queryset = queryset.filter(foods__isnull=False)
        return queryset.distinct().order_by("name")
