from django.core.exceptions     import PermissionDenied
from django.db.models           import Count

from rest_framework             import viewsets
from rest_framework.decorators  import api_view, action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response    import Response

from common.decorators          import api_arg, api_model_arg
from common.permissions         import IsAdminOrReadOnlyList
from common.permissions         import Or, ReadOnly, ReadWrite

from recipe_mgr.models          import Food, Ingredient, FoodConversion, CookingMethod, RawState, Recipe

from recipe_mgr.serializers     import FoodSerializer, IngredientSerializer,\
                                       NewIngredientSerializer, FoodConversionSerializer,\
                                       CookingMethodSerializer, RawStateSerializer, QuickRecipeSerializer

import json

class RawStateViewSet(viewsets.ModelViewSet):
    queryset = RawState.objects.all()
    serializer_class = RawStateSerializer
    permission_classes = (IsAdminOrReadOnlyList, )

class CookingMethodViewSet(viewsets.ModelViewSet):
    queryset = CookingMethod.objects.all()
    serializer_class = CookingMethodSerializer
    permission_classes = (IsAdminOrReadOnlyList, )

    @staticmethod
    @api_view(['GET'])
    @api_model_arg("food", Food)
    def food(request, food):
        results = []
        food_cooking_methods_ids = tuple(r[0] for r in food.food_nutrients.values_list('cooking_method_id').annotate())
        for cooking_method in CookingMethod.objects.all():
            results.append(CookingMethodSerializer(cooking_method).data)
            results[-1]["available"] = cooking_method.id in food_cooking_methods_ids
        return Response(results, 200)

class FoodConversionViewSet(viewsets.ModelViewSet):
    serializer_class = FoodConversionSerializer
    permission_classes = (IsAdminOrReadOnlyList, )

    @api_arg('unit', str, None)
    @api_model_arg('food', Food, allow_none=True)
    def get_queryset(self, unit, food):
        queryset = FoodConversion.objects.all()
        if self.request.method in ('PUT',):
            return queryset
        if food is not None:
            queryset = queryset.filter(food=food)
        if unit is not None:
            queryset = queryset.filter(unit=unit)
        return queryset

    def update(self, request, pk=None):
        """
        Override the update : we want to check if the conversion value has changed
        if so, we want to apply the new conversion to all the ingredients that used
        this conversion as default
        """
        previous_value = self.get_object().value
        res = super(viewsets.ModelViewSet, self).update(request, pk)
        new_value = self.get_object().value
        if previous_value != new_value:
            # Conversion value has changed, apply change to ingredients
            # already using this conversion
            for ingredient in Ingredient.objects.filter(default_conversion_id = pk):
                ingredient.grams *= float(new_value) / previous_value
                ingredient.save()
        return res

    def destroy(self, request, pk = None):
        """
        Override the destroy : we want to check if the foodconversion is not used in any recipe
        """
        if Ingredient.objects.filter(default_conversion_id=pk).count() > 0:
            return Response({"status": "error", "message": "this conversion is used in ingredients"}, 200)
        return super().destroy(request, pk)


    @action(detail=True, methods=['get'])
    def recipes(self, request, pk):
        """
        Return the list of recipes (id/name) used by this conversion
        """
        conversion = self.get_object()
        recipes_by_id = {}
        for ingredient in conversion.ingredients.select_related('recipe').all():
            recipe = ingredient.recipe
            recipes_by_id[recipe.id] = recipe

        recipes = sorted(recipes_by_id.values(), key=lambda x: x.name)

        return Response(QuickRecipeSerializer(recipes, many = True).data)

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (Or(ReadWrite("admin"), ReadWrite(user = ("recipe", "author")), ReadOnly()), )

    def get_serializer_class(self):
        # See Ugly fix in NewIngredientSerializer
        if self.request.method not in SAFE_METHODS:
            return NewIngredientSerializer
        else:
            return IngredientSerializer

    @classmethod
    def _get_default_raw_state(cls, food):
        if food.default_raw_state is not None:
            return food.default_raw_state_id
        if food.food_nutrients.count() > 0:
            query = food.food_nutrients.all()
            # Grouping by nutrient count
            query = query.values("raw_state").annotate(nb_nutrients = Count("raw_state"))
            # Ordering by decreasing nutrient counts
            query = query.order_by('-nb_nutrients')
            # Returning raw state id with higher nutrient number
            return query[0]['raw_state']
        # Hopeless
        return RawState.objects.get(name = "frais").id

    @classmethod
    def _get_default_conversion(cls, food):
        generic_units = ('ml', 'litre', 'g', 'mg')
        if food.default_conversion is not None:
            return food.default_conversion_id
        if food.conversions.count() == 1:
            return food.conversions.get().id
        for conversion in food.conversions.all():
            for generic_unit in generic_units:
                if conversion.unit == generic_unit:
                    break
            else:
                return conversion.id
        # Hopeless
        return food.conversions.all()[0].id

    @classmethod
    def _get_default_cooking_method(cls, food):
        if food.default_cooking_method is not None:
            return food.default_cooking_method_id
        if food.food_nutrients.count() > 0:
            query = food.food_nutrients.all()
            # Grouping by nutrient count
            query = query.values("cooking_method").annotate(nb_nutrients = Count("cooking_method"))
            # Ordering by decreasing nutrient counts
            query = query.order_by('-nb_nutrients')
            # Returning cooking method id with higher nutrient number
            return query[0]['cooking_method']
        # Hopeless
        return CookingMethod.objects.get(name = "cru").id

    def _clear_cached_recipe(self, request):
        recipe_id = request.data.get('recipe', None)
        if recipe_id:
            recipe = Recipe.objects.get(pk = recipe_id)
        else:
            ingredient = self.get_object()
            recipe = ingredient.recipe

        if recipe is not None:
            if recipe.author_id != request.user.id and not request.user.is_admin:
                raise PermissionDenied
            # Clearing cached value
            recipe.clear_cached()

    def create(self, request, *args, **kargs):
        self._clear_cached_recipe(request)
        return super().create(request, *args, **kargs)

    def update(self, request, *args, **kargs):
        self._clear_cached_recipe(request)
        return super().update(request, *args, **kargs)

    def destroy(self, request, *args, **kargs):
        self._clear_cached_recipe(request)
        return super().destroy(request, *args, **kargs)

    @action(detail=True, methods=['post'])
    def set_cooking_method(self, request, pk):
        params = json.loads(request.body.decode("utf-8"))
        if 'cooking_method_id' not in params:
            return Response({"error": "cooking_method_id not set"}, 400)

        ingredient = self.get_object()
        ingredient.cooking_method_id = int(params['cooking_method_id'])
        ingredient.save()
        self._clear_cached_recipe(request)
        return Response(status=200)

    @action(detail=True, methods=['post'])
    def set_previously_cooked(self, request, pk):
        params = json.loads(request.body.decode("utf-8"))
        if 'previously_cooked' not in params:
            return Response({"error": "previously_cooked not set"}, 400)
        previously_cooked = params['previously_cooked']
        if previously_cooked not in ("yes", "no"):
            return Response({"error": "previously_cooked should  be 'yes' or 'no'"}, 400)

        ingredient = self.get_object()
        ingredient.previously_cooked = previously_cooked == "yes"
        ingredient.save()
        self._clear_cached_recipe(request)
        return Response(status=200)
