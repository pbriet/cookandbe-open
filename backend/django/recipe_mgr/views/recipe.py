from django.core.exceptions             import PermissionDenied
from django.db.models                   import Count, Q
from django.utils                       import timezone

from rest_framework                     import viewsets
from rest_framework.decorators          import api_view, action, permission_classes
from rest_framework.permissions         import AllowAny
from rest_framework.response            import Response

from common.decorators                  import api_arg, api_model_arg, api_check_user_id
from common.image                       import upload_image, no_photo_modifications
from common.model                       import reload_object
from common.permissions                 import IsAdminOrOwnerElseReadOnly, IsAdminOrReadOnlyList
from common.permissions                 import Or, ReadOnly, ReadWrite, Allow
from common.rest                        import TreeLikeViewSetMixin, AddRemoveManyToManyViewSetMixin, CustomViewSet

from emailing.tools                     import sendmail_template, MessageType

from hippocrate.models.recipestorage    import MainRecipeStorage

from nutrient.helpers                   import RecipeNutrientCalculator
from nutrient.models                    import Nutrient
from nutrient.serializers               import NutrientSerializer

from recipe_mgr.controller              import get_full_recipe_serialization, RecipeImageGenerator
from recipe_mgr.models                  import Recipe, RecipeTag, RecipeInstruction, DishType, Ustensil, FoodTag
from recipe_mgr.serializers             import PartialRecipeSerializer, RecipeTagSerializer,\
                                               QuickRecipeSerializer, FullRecipeSerializer, \
                                               RecipeInstructionSerializer, RecipeIngredientSerializer,\
                                               DishTypeSerializer, ReviewRecipeSerializer,\
                                               FoodTagSerializer

from recipe_mgr.seasons                 import SeasonManager

import random
import copy

from optalim.log import logger

@api_view(['GET'])
@api_arg('author_id', int, None)
def count_recipe(request, author_id, *args, **kargs):
    if author_id is None:
        raise PermissionDenied
    return secure_count_recipe(request, author_id, *args, **kargs)

@api_view(['GET'])
@api_arg('author_id', int, None)
@api_arg('dimension', str, None)
@api_arg('keyword', str, None)
def secure_count_recipe(request, author_id, dimension, keyword):
    query = Recipe.objects.all()
    if author_id:
        query = query.filter(author_id = author_id)
    if keyword:
        query = query.filter(name__icontains = keyword)
    # Without subquery
    if dimension is None:
        return Response({"result": query.count()})

    # With subquery
    AUTHORIZED_DIMENSIONS = ['dish_types', 'author']

    if dimension not in AUTHORIZED_DIMENSIONS:
        return Response({"error": "dimension should be one of the following values: %s" % AUTHORIZED_DIMENSIONS}, 400)

    # Returning values per dimension values
    # The following is an equivalent of SELECT dimension, COUNT(*) FROM recipe GROUP BY dimension
    values = query.values(dimension).order_by().annotate(Count(dimension))
    res = {}
    dimension_count_field = dimension + '__count'  # This is the name of the count returned by the Django query
    for val in values:
        if val[dimension_count_field] == 0:
            continue
        # Converting
        res[val[dimension]] = val[dimension_count_field]  # (value, count)
    return Response({"result": res})

@api_view(['GET'])
@permission_classes((AllowAny,))
@api_arg('offset', int, 0)
@api_arg('limit', int, 10)
@api_arg('dish_type_ids', int, None, is_list=True)
@api_arg('keyword', str, None)
@api_arg('author_id', int, None)
@api_arg('details', str, None)
@api_arg('min_status', int, None)
@api_arg('include_own_recipes', bool, True)
@api_arg('order_by', str, None)
@api_arg('advanced_recipes_only', bool, False)
def recipe_search(request, keyword, dish_type_ids, limit, offset, author_id, details,
                  min_status, include_own_recipes, advanced_recipes_only, order_by):
    """
    @param include_own_recipes: include the recipes of the logged in user (if there's one) in the results
    @param advanced_recipes_only: filter recipes with at least 4 ingredients
    """
    # Securité pour prévenir la récupération de trop de données d'un seul coup
    if limit > 20:
        raise PermissionDenied
    if min_status is None and author_id is None:
        min_status = Recipe.STATUS_PUBLISHED
    query = Recipe.objects.filter(internal = False)
    if keyword:
        for word in keyword.split(' '):
            query = query.filter(name__unaccent__icontains = word)
    if dish_type_ids:
        query = query.filter(dish_types__id__in=dish_type_ids).distinct()
    if author_id:
        query = query.filter(author_id = author_id)
    if order_by not in ('name', 'creation_date', '-creation_date'):
        assert order_by is None, "Invalid order_by value: %s" % order_by
        order_by = 'name'
    if min_status:
        status_filter = Q(status__gte=min_status)
        if include_own_recipes:
            if request.user is None:
                return Response({"error": "asking for user recipes while not logged in"}, 400)
            status_filter = status_filter | Q(author_id = request.user.id, status__gte=Recipe.STATUS_VALIDATED)
        query = query.filter(status_filter)
    if advanced_recipes_only:
        query = query.annotate(nb_ingredients = Count('ingredients')).\
                      filter(nb_ingredients__gte=4)
    query = query.order_by(order_by)
    # Some stats
    count = query.count()
    if details in ("full", "ingredients"):
        query = query.prefetch_related('ingredients', 'ingredients__food')
    if details == "full":
        query = query.prefetch_related('ingredients__default_conversion')
    # Results
    recipes = query[offset:offset+limit]
    if details == "full":
        logger.warning("WARNING/FIXME: Django rest is making too many queries")
        data = PartialRecipeSerializer(recipes, many = True).data
    elif details == "ingredients":
        data = RecipeIngredientSerializer.serialize(recipes)
    else:
        data = QuickRecipeSerializer(recipes, many = True).data

    return Response({"results": data, "count" : count, "keyword" : keyword}, 200)

@api_view(['GET'])
@api_arg('ids_only', bool, False)
@api_check_user_id
def list_personal_recipes(request, user_id, ids_only):
    query = Recipe.objects.filter(internal = False, author_id = user_id).order_by('-creation_date')
    if ids_only:
        data = [r.id for r in query.only('id')]
    else:
        query.prefetch_related('ingredients', 'ingredients__food')
        data = RecipeIngredientSerializer.serialize(query)
    return Response({"results": data, "count" : len(data)}, 200)



@api_view(['GET'])
@api_arg('offset', int, 0)
@api_arg('limit', int, 10)
@api_model_arg('food_tag', FoodTag)
@permission_classes((AllowAny,))
def recipes_from_food_tag(request, food_tag, offset, limit):
    # Retrieving the food_tag hierarchy
    food_tags = food_tag.get_children(including_self=True)
    # Filtering recipes that have ingredient containing this food_tag
    query = Recipe.objects.filter(status=Recipe.STATUS_PUBLISHED).filter(ingredients__food__food_tags__in=food_tags,
                                                                         ingredients__grams__gte=50)

    count = query.count()
    recipes = query[offset:offset+limit]
    # Serializing
    data = RecipeIngredientSerializer.serialize(recipes)
    return Response({"results": data, "count" : count}, 200)

@api_view(['GET'])
@api_arg('ids', int, is_list=True)
@api_arg('serializer', str)
def recipes_get_many(request, ids, serializer):
    """
    Return a list of serialized recipes from ids
    """
    if serializer == "full":
        return  Response(get_full_recipe_serialization({'pk__in': ids}, many=True))
    recipes = Recipe.objects.filter(pk__in=ids).prefetch_related('ingredients', 'ingredients__food',
                                                                 'ingredients__default_conversion')
    if serializer == "partial":
        data = PartialRecipeSerializer(recipes, many = True).data
    elif serializer == "ingredients":
        data = RecipeIngredientSerializer.serialize(recipes)
    else:
        data = QuickRecipeSerializer(recipes, many = True).data
    return Response(data)

class RecipeInstructionViewSet(viewsets.ModelViewSet):
    queryset = RecipeInstruction.objects.all()
    serializer_class = RecipeInstructionSerializer
    permission_classes = (IsAdminOrOwnerElseReadOnly("recipe", "author"), )

class RecipeTagViewSet(TreeLikeViewSetMixin, viewsets.ModelViewSet):
    queryset = RecipeTag.objects.all()
    serializer_class = RecipeTagSerializer
    permission_classes = (IsAdminOrReadOnlyList, )

class RecipeViewSet(CustomViewSet, AddRemoveManyToManyViewSetMixin):
    model = Recipe
    exclude = []
    filtered_fields = ("author_id", "dish_type_id")
    permission_classes = (Or(ReadWrite("admin", list = True), ReadWrite(user = ("author", )), ReadOnly(list = True)), )

    details = property(lambda s: s.request.query_params.get('details', None))

    def _quick_serialization(self):
        return self.request.method == 'GET' and 'pk' not in self.kwargs and self.details is None

    def get_serializer_class(self):
        if self._quick_serialization():
            # Means we are displaying a list of objects
            return QuickRecipeSerializer
        elif self.details == "full":
            return FullRecipeSerializer
        elif self.details == "review":
            return ReviewRecipeSerializer
        assert self.details != "ratio"
        return PartialRecipeSerializer

    @api_arg('include_internal', bool, False)
    def get_queryset(self, include_internal):
        author_id = self.request.query_params.get('author_id', None)
        dish_type_id = self.request.query_params.get('dish_type_id', None)
        status = self.request.query_params.get('status', None)
        queryset = Recipe.objects.all()
        if not include_internal:
            queryset = queryset.filter(internal=False)
        if not self._quick_serialization():
            queryset.prefetch_related('ingredients', 'ingredients__default_conversion', 'ingredients__food')
        if author_id is not None:
            queryset = queryset.filter(author_id = author_id)
        if dish_type_id is not None:
            queryset = queryset.filter(dish_types__id = dish_type_id)
        if status is not None and status in Recipe.STATUS_DICT:
            queryset = queryset.filter(status = Recipe.STATUS_DICT[status])
        queryset = queryset.order_by('name')
        return queryset

    @api_arg('nutrient_ids', int, None, is_list=True)
    def list(self, request, nutrient_ids, **kwargs):
        response = super(RecipeViewSet, self).list(request, **kwargs)
        if nutrient_ids is not None:
            objs = Nutrient.objects.filter(pk__in=nutrient_ids)
            for serialized_recipe in response.data:
                recipe_id = int(serialized_recipe['id'])
                # Jim 13/03/2014: used to display recipe nutrients according to the user's ratio (unknown for now so 1.0)
                ratio = 1.0
                nutrients = dict((n.id, MainRecipeStorage.get(recipe_id).get_data_from_key(n.key, ratio)) for n in objs)
                serialized_recipe['nutrients'] = nutrients
        return response

    @action(detail=True, methods=['get'])
    @api_arg('ratio', float, None)
    @api_arg('pk', int)
    def with_ingredients(self, request, pk, ratio):
        """
        Returns the recipe infos "displayable", with the correct ratios and values
        """
        res = get_full_recipe_serialization({'pk': pk}, ratio=ratio)
        return Response(res)

    @action(detail=True, methods=['get'])
    @api_arg('ratio', float, 1)
    def nutrients(self, request, pk, ratio):
        recipe = self.get_object()
        calculator = RecipeNutrientCalculator(recipe)
        calculator.compute()

        res = {}
        nutrients = Nutrient.objects.all()
        nutrients = dict((n.id, n) for n in nutrients)
        for nutrient_id, value in calculator.aggregated_nutrients.items():
            nutrient = nutrients[nutrient_id]
            res[nutrient.name] = {"nutrient": NutrientSerializer(nutrient).data,
                                  "value": value * ratio,
                                  "data_availability": round(calculator.nutrients_data_availability[nutrient_id], 2)}
        return Response(res)


    @action(detail=True, methods=['get'])
    def get_suggested_food_tags(self, request, pk):
        """
        Returns the relevant food tags with their details for this recipe
        """
        recipe = self.get_object()

        suggested_food_tag_ids = list(MainRecipeStorage.get(recipe.id).suggested_food_tag_ids)
        suggested_food_tags = FoodTag.objects.filter(pk__in=suggested_food_tag_ids)
        return Response(FoodTagSerializer(suggested_food_tags, many=True).data)



    @action(detail=True, methods=['get'])
    def dish_types(self, request, pk):
        """
        Returns dish types of 1 recipe
        """
        recipe = self.get_object()
        return Response(DishTypeSerializer(recipe.dish_types.all(), many=True).data)

    @action(detail=True, methods=['post'])
    def add_dish_type(self, request, pk):
        """
        Add one dish type to a recipe
        """
        res = self._add_many_object(request, DishType, 'dish_types', 'dish_type_id', reverse_key='recipe_id')
        self.get_object().clear_cached()
        return res

    @action(detail=True, methods=['post'])
    def remove_dish_type(self, request, pk):
        """
        remove one dish type to a recipe
        """
        recipe = self.get_object()
        # if recipe.dish_types.count() <= 1:
        #     return Response({"error": "there must be at least on dish_type remaining - add another dish_type first"}, status=400)
        res = self._remove_many_object(request, DishType, 'dish_types', 'dish_type_id', reverse_key='recipe_id')
        self._post_deletion_dish_type_update(recipe)
        return res

    def _post_deletion_dish_type_update(self, recipe):
        """
        After removing one or more dish_types on a recipe, ensure that the existing
        dishes with dishrecipe assigned to _this_ recipe are still correct.
        If not, update the dish_type of the dish
        """
        reload_object(recipe)
        valid_dishtype_ids = [dt.id for dt in recipe.dish_types.all()]
        for dishrecipe in recipe.dishrecipe_set.prefetch_related('dish__dish_type').all():
            dish = dishrecipe.dish
            dish_type = dish.dish_type
            dish_dishrecipes = list(dish.dishrecipe_set.all())
            if len(dish_dishrecipes) == 1 and dish_type.id not in valid_dishtype_ids:
                # There is a dish that must be changed
                dishrecipe.dish.dish_type_id = valid_dishtype_ids[0]
                dishrecipe.dish.save()
            elif len(dish_dishrecipes) > 1:
                # Within an aggregated dish : splitting the dish into multiple ones
                for i, sub_dishrecipe in enumerate(dish_dishrecipes):
                    new_dish = copy.copy(dish)
                    new_dish.id = None
                    new_dish.order = i
                    new_dish.dish_type = sub_dishrecipe.recipe.dish_types.first()
                    new_dish.save()
                    sub_dishrecipe.order = i
                    sub_dishrecipe.dish = new_dish
                    sub_dishrecipe.save()
                dish.delete()

        recipe.clear_cached()

    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk):
        """
        Add one dish type to a recipe
        """
        return self._add_many_object(request, RecipeTag, 'tags', 'tag_id')

    @action(detail=True, methods=['post'])
    def remove_tag(self, request, pk):
        """
        remove one dish type to a recipe
        """
        return self._remove_many_object(request, RecipeTag, 'tags', 'tag_id')

    @action(detail=True, methods=['post'])
    def add_ustensil(self, request, pk):
        """
        Add one ustensil to a recipe
        """
        return self._add_many_object(request, Ustensil, 'ustensils', 'ustensil_id')

    @action(detail=True, methods=['post'])
    def remove_ustensil(self, request, pk):
        """
        remove one ustensil to a recipe
        """
        return self._remove_many_object(request, Ustensil, 'ustensils', 'ustensil_id')

    def destroy(self, request, pk = None):
        """
        Override the destroy : we want to check if the status allows recipe deletion.
        """
        recipe = Recipe.objects.get(pk = pk)
        if recipe.status > Recipe.STATUS_VALIDATED and not request.user.is_admin:
            raise PermissionDenied
        return super(viewsets.ModelViewSet, self).destroy(request, pk)

    @no_photo_modifications('photo')
    def update(self, data):
        """
        Override the update : we want to check if the status value has changed.
        If so, we want to apply the new status only if the user is allowed to do so.
        """
        data = dict(data.items())
        current_recipe = self.get_object()
        # Protecting system attributes
        for attrName in Recipe.SYSTEM_ATTRIBUTES:
            data[attrName] = getattr(current_recipe, attrName)

        # Needed but readonly after creation
        data["author"] = current_recipe.author
        # Retrieving status
        old_status = current_recipe.status
        new_status = data.get('status')
        if new_status is not None:
            data.update(self._check_status(int(new_status), old_status))
        # Clearing cached value
        current_recipe.clear_cached()
        # Updating DB object
        serializer = self.get_serializer(self.get_object(), data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if current_recipe.auto_photo:
            RecipeImageGenerator(current_recipe.id)()

        return Response(serializer.data)

    def perform_create(self, serializer):
        status = self.request.data.get('status', Recipe.STATUS_CREATING)
        data = self._check_status(status)
        serializer.save(**data)

    def _check_status(self, new_status, old_status = None):
        """
        Check recipe status according to privileges.
        """
        new_status = int(new_status)
        if old_status: old_status = int(old_status)
        if new_status == Recipe.STATUS_PUBLISHED and not self.request.user.is_admin:
            # User trying to publish recipe
            raise PermissionDenied
        if old_status == new_status:
            # No change
            return {}
        if old_status is not None and old_status >= Recipe.STATUS_REVIEWING and not self.request.user.is_admin:
            # User trying to change published recipe
            raise PermissionDenied
        if new_status == Recipe.STATUS_PUBLISHED:
            return {"publication_date": str(timezone.now()),
                    "publisher": self.request.user}
        return {}

    @action(detail=True, methods=['post'])
    @api_arg('image', str)
    def upload_img(self, request, pk, image):
        """
        Updates the image attached to the recipe
        """
        recipe = Recipe.objects.get(pk=pk)
        upload_image(image, recipe, 'photo')
        recipe.auto_photo = False
        recipe.save()
        return Response({"status": "ok"})

@api_view(['GET'])
@permission_classes((AllowAny,))
@api_arg('key', str)
def recipe_from_key(request, key):
    """
    Returns a full serialization of a recipe, from its url_key
    """
    res = get_full_recipe_serialization({'url_key': key})
    if res is None:
        return Response({"exists": False}, 200)
    res["exists"] = True
    return Response(res)

@api_view(['POST'])
@permission_classes((Allow('reviewer'),))
@api_arg('reason', str)
@api_model_arg('recipe', Recipe)
def recipe_reject_publication(request, recipe, reason):
    """
    Reject the publication of a given recipe
    """
    if recipe.status != Recipe.STATUS_REVIEWING:
        return Response({"error": "Cannot reject a recipe which is not in 'reviewing' status"}, status=400)
    recipe.status = Recipe.STATUS_VALIDATED
    recipe.save()
    sendmail_template(MessageType.MAIN_INFO, 'recipe_mgr/templates/rejected_publication.html', {'reason': reason, 'recipe': recipe},
                        'La publication de votre recette a été refusée', users=[recipe.author], tags=["recipe_reject_publication"])
    return Response({"status": "ok"})


@api_view(['POST'])
@permission_classes((Allow('reviewer'),))
@api_model_arg('recipe', Recipe)
def duplicate_private_recipe(request, recipe):
    """
    Duplicate a recipe, marking it reviewed, and set author as current user  (reviewer)
    """
    clone = Recipe.clone(recipe)
    clone.author = request.user
    clone.reviewed = True
    clone.save()

    recipe.reviewed = True
    recipe.save()

    return Response({"status": "ok", 'recipe_id': clone.pk})


@api_view(['POST'])
@permission_classes((Allow('reviewer'),))
@api_model_arg('recipe', Recipe)
def mark_private_recipe_as_reviewed(request, recipe):
    """
    Mark a private recipe as being reviewed (thus not duplicated)
    """
    recipe.reviewed = True
    recipe.save()
    return Response({"status": "ok"})


@api_view(['GET'])
@api_arg('nb_recipes', int, 6)
@api_arg('only_with_photo', bool, True)
@permission_classes((AllowAny,))
def random_season_recipe_selection(request, nb_recipes, only_with_photo):
    """
    Returns X random recipes compatible with current season
    """
    season_recipe_ids = SeasonManager.get_cached_seasonal_recipe_ids()

    # At least 4 ingredients
    query = Recipe.objects.all().annotate(nb_ingredients = Count('ingredients'))
    if only_with_photo:
        query = query.filter(auto_photo=False)
    query = query.filter(nb_ingredients__gte=4).only('id')

    nice_recipe_ids = set(r.id for r in query)
    recipe_ids = season_recipe_ids.intersection(nice_recipe_ids)
    if len(recipe_ids) > nb_recipes:
        recipe_ids = random.sample(recipe_ids, nb_recipes)

    query = Recipe.objects.prefetch_related('ingredients', 'ingredients__food').filter(pk__in=recipe_ids)
    data = RecipeIngredientSerializer.serialize(list(query))

    return Response({"results": data}, 200)

@api_view(['POST'])
@permission_classes((Allow('reviewer'),))
@api_model_arg('recipe', Recipe)
def recipe_publish(request, recipe):
    """
    Publish a recipe : set its status to PUBLISHED and send a "congrats" email to the author
    """
    if recipe.status != Recipe.STATUS_REVIEWING:
        return Response({"error": "Cannot publish a recipe which is not in 'reviewing' status"}, status=400)
    recipe.status = Recipe.STATUS_PUBLISHED
    recipe.save()
    sendmail_template(MessageType.MAIN_INFO, 'recipe_mgr/templates/publication.html', {'recipe': recipe},
                        'Félicitations : votre recette a été publiée', users=[recipe.author],
                        tags=["recipe_congrats_publication"])
    return Response({"status": "ok"})


@api_view(['GET'])
@permission_classes((Allow('reviewer'),))
def private_to_review(request):
    """
    Returns the list of private recipes to be reviewed
    """
    recipes = Recipe.objects.filter(status=Recipe.STATUS_VALIDATED,
                                    author__user_roles=None,
                                    internal=False,
                                    reviewed=False)

    nb_recipes = recipes.count()

    data = QuickRecipeSerializer(recipes[:100], many = True).data
    return Response({'data': data, 'nb': nb_recipes})