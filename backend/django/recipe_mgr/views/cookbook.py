
from rest_framework                     import viewsets
from rest_framework.decorators          import api_view
from rest_framework.response            import Response
from common.decorators                  import api_arg, api_check_user_id
from common.permissions                 import IsOwner

from recipe_mgr.models                  import CookbookRecipe
from recipe_mgr.serializers             import CookbookRecipeSerializer

class CookbookRecipeViewSet(viewsets.ModelViewSet):
    model = CookbookRecipe
    exclude = []
    serializer_class = CookbookRecipeSerializer
    permission_classes = (IsOwner("user", list = True), )

    def get_queryset(self):
        user_id = int(self.kwargs['user_id'])
        return CookbookRecipe.objects.filter(user_id = user_id).order_by('recipe__name')

@api_view(['GET'])
@api_check_user_id
def count_cookbook_recipes(request, user_id):
    return Response({"nb": request.user.cookbook_recipes.count()})

@api_view(['POST'])
@api_arg('recipe_id', int)
@api_check_user_id
def delete_cookbook_recipe_by_recipe(request, user_id, recipe_id):
    try:
        cookbook_recipe = request.user.cookbook_recipes.get(recipe_id=recipe_id)
    except CookbookRecipe.DoesNotExist:
        return Response({"status": "error", "error": "no such recipe in cookbook"}, 400)
    cookbook_recipe.delete()
    return Response({"status": "ok"})