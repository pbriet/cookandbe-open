
from django.db.models           import Count
from django.core.exceptions     import PermissionDenied

from rest_framework             import viewsets
from rest_framework.decorators  import api_view, action, permission_classes
from rest_framework.permissions import AllowAny, SAFE_METHODS
from rest_framework.response    import Response

from common.decorators          import api_arg, api_model_arg
from common.image               import upload_image, no_photo_modifications
from common.permissions         import IsAdminOrReadOnlyList, IsAdminOrReadOnly
from common.rest                import CustomViewSet

from recipe_mgr.models          import Food, FoodTag, FoodTagSet
from recipe_mgr.serializers     import FoodSerializer, FoodTagSerializer, FoodTagSerializerWithNb, FoodTagSetSerializer, FoodTagSetWritableSerializer

from optalim.log import logger

@api_view(['GET'])
@api_arg('offset', int, 0)
@api_arg('limit', int, 50)
@api_arg('include_disabled', bool, True)
def untagged_food(request, offset, limit, include_disabled):
    """
    Returns a list of food that are in less than two food_tags,
    sorted by popularity (occurences in recipes)
    """
    foods = Food.objects.annotate(nb_ingredients = Count('ingredient'), nb_tags = Count('tagsets'))
    foods = foods.filter(nb_tags__lt=2).order_by('-nb_ingredients')
    if not include_disabled:
        foods = foods.filter(enabled=True)
    foods = foods.prefetch_related('tagsets__tag')
    foods = foods[offset:limit]

    res = []
    for food in foods:
        res.append({"name": food.name, "id": food.id, "enabled": food.enabled,
                    "nb_ingredients": food.nb_ingredients,
                    "tags": [FoodTagSerializer(tagset.tag).data for tagset in food.tagsets.all()]})

    return Response({"data": res})

@api_view(['GET'])
@api_arg('keyword', str)
@api_arg('allow_non_dislikables', bool, False)
def food_tag_search(request, keyword, allow_non_dislikables):
    filterKargs = {
        'name__unaccent__icontains': keyword,
    }
    if not allow_non_dislikables:
        filterKargs['can_be_disliked'] = True
    else:
        if not request.user.is_authenticated or True not in (request.user.is_admin, request.user.is_operator):
            raise PermissionDenied
    foodTags = FoodTag.objects.filter(**filterKargs)
    if foodTags.count() > 20 and len(keyword) <= 2:
        return Response({
            "food_tags": [],
            "empty": False
        })

    foodTags = foodTags.annotate(nb_food = Count('food')).extra(select={'length':'Length("recipe_mgr_foodtag"."name")'}).order_by('length')

    serializer = FoodTagSerializerWithNb(foodTags, many = True)
    res = {
        "food_tags": serializer.data,
        "empty": (len(foodTags) == 0)
        }
    return Response(res)


@api_view(['GET'])
@api_arg('key', str)
@permission_classes((AllowAny,))
def food_tag_from_key(request, key):
    try:
        food_tag = FoodTag.objects.get(url_key=key)
    except FoodTag.DoesNotExist:
        return Response({"exists": False}, 200)
    res = FoodTagSerializer(food_tag).data
    res["exists"] = True
    return Response(res)


class FoodTagViewSet(viewsets.ModelViewSet):
    serializer_class = FoodTagSerializer
    permission_classes = (IsAdminOrReadOnlyList, )

    @api_model_arg('food', Food, allow_none=True)
    @api_arg('include_parents', bool, None)
    @api_arg('dislikable_only', bool, False)
    def get_queryset(self, food, include_parents, dislikable_only):
        if include_parents is None:
            include_parents = food is not None
        if food is None:
            queryset = FoodTag.objects.all()
        else:
            queryset = FoodTag.objects.filter(foods__id=food.id)
        if dislikable_only:
            queryset = queryset.filter(can_be_disliked=True)
        queryset = queryset.prefetch_related('foods')
        if food is not None:
            queryset = sorted(list(queryset), key=lambda x: x.foods.count())
        if not include_parents:
            return queryset
        res = set()
        for food_tag in list(queryset):
            res.add(food_tag)
            parent_ids = food_tag.cached_parents_ids()
            for parent_food_tag in FoodTag.objects.filter(pk__in=parent_ids).prefetch_related('foods'):
                res.add(parent_food_tag)

        if food is not None and include_parents and not dislikable_only and len(res) < 2:
            # Not good : there is less than 2 food_tags attached to a food. Report it.
            logger.critical("Food with too few food tags : %s (id=%s) (nb=%i)" % (food.name, food.id, len(res)))

        return sorted(res, key=lambda x: x.foods.count())


    @no_photo_modifications('photo')
    def update(self, data):
        """
        Override the update : we want to check if the status value has changed.
        If so, we want to apply the new status only if the user is allowed to do so.
        """
        # Updating DB object
        serializer = self.get_serializer(self.get_object(), data=data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    @api_arg('image', str)
    def upload_img(self, request, pk, image):
        """
        Updates the image attached to the food_tag
        """
        food_tag = FoodTag.objects.get(pk=pk)
        upload_image(image, food_tag, 'photo')
        return Response({"status": "ok"})

    @action(detail=True, methods=['get'])
    def parents(self, request, pk):
        parents = self.get_object().parents.all()
        return Response(FoodTagSerializer(parents, many=True).data)

    @action(detail=True, methods=['get'])
    def children(self, request, pk):
        children = self.get_object().children.all()
        return Response(FoodTagSerializer(children, many=True).data)

    @action(detail=True, methods=['post'])
    @api_model_arg('food_tag', FoodTag)
    def add_child(self, request, pk, food_tag):
        obj = self.get_object()
        if obj.children.filter(pk=food_tag.id).count():
            return Response({"error": "already added"}, 400)
        obj.children.add(food_tag)
        return Response({"status": "added"}, 200)

    @action(detail=True, methods=['post'])
    @api_model_arg('food_tag', FoodTag)
    def remove_child(self, request, pk, food_tag):
        obj = self.get_object()
        if obj.children.filter(pk=food_tag.id).count() == 0:
            return Response({"error": "not a child"}, 400)
        obj.children.remove(food_tag)
        return Response({"status": "removed"}, 200)

    @action(detail=True, methods=['get'])
    def find_anomalies(self, request, pk):
        """
        From all the foods that are contained into the current food tag,
        find whether there is no other food tag that contains part of the foods
        -> i.e. this food tag should be a child, instead of having directly the foods
        """
        obj = self.get_object()
        foods = obj.foods.all().prefetch_related("food_tags")
        food_ids = set([f.id for f in foods])

        # Retrieving the food tags that match at least one food in the current food tag
        other_food_tags = {}
        for food in foods:
            for other_ft in food.food_tags.all():
                other_food_tags[other_ft.id] = other_ft

        # Food tags that should be included
        should_be_included = []

        if len(other_food_tags):
            del other_food_tags[obj.id]
        # For each food tag, checking if all the foods of this food tag are in the current food tag
        for other_ft in other_food_tags.values():
            other_ft_food_ids = set([f.id for f in other_ft.foods.all()])
            if food_ids.issuperset(other_ft_food_ids):
                should_be_included.append(other_ft)

        # Formatting the response
        res = []
        for food_tag in should_be_included:
            res.append({"food_tag": {"id": food_tag.id, "name": food_tag.name},
                        "foods": [{"id": food.id, "name": food.name} for food in food_tag.foods.all()]})

        return Response({"suggested_modifications": res})

class FoodTagSetViewSet(CustomViewSet):
    model = FoodTagSet
    exclude = []
    filtered_fields = ('tag_id', 'food_id')
    permission_classes = (IsAdminOrReadOnly, )

    def get_serializer_class(self):
        if self.request.method not in SAFE_METHODS:
            if type(self.request.data['food']) is dict:
                self.request.data['food'] = self.request.data['food']['id']
            return FoodTagSetWritableSerializer
        return FoodTagSetSerializer


