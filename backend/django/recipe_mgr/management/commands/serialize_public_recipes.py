from django.core.management.base    import BaseCommand
from django.core import serializers
from django.utils import timezone

from recipe_mgr.models              import Recipe, RecipeInstruction, Ingredient, RecipeDishType

from user_mgr.models                import User, BaseUser

class Command(BaseCommand):
    args = ''
    help = 'Dump public recipes in a json file. Along with the "main" user optalim'

    def handle(self, *args, **options):

        optalim = User.objects.get(email="optalim@gmail.com")
        optalim_base = BaseUser.objects.get(email="optalim@gmail.com")
        optalim_roles = optalim_base.user_roles.all()

        optalim_meta_planning = optalim.meta_planning
        optalim_profiles = optalim.profile_set.all()
        optalim_eaters = optalim.eaters.all()

        recipes = list(Recipe.objects.filter(status=Recipe.STATUS_PUBLISHED))
        ingredients = Ingredient.objects.filter(recipe__status=Recipe.STATUS_PUBLISHED)
        instructions = RecipeInstruction.objects.filter(recipe__status=Recipe.STATUS_PUBLISHED)
        dts = RecipeDishType.objects.filter(recipe__status=Recipe.STATUS_PUBLISHED)

        for recipe in recipes:
            recipe.author = optalim
            recipe.publisher = optalim

        class AllItemsIterator(object):
            def __iter__(self):
                print("start")
                yield optalim_base
                yield optalim
                yield optalim_meta_planning
                yield from optalim_profiles
                yield from optalim_roles
                yield from optalim_eaters
                print("-> recipes")
                yield from recipes
                print("-> ingredients")
                yield from ingredients
                print("-> instructions")
                yield from instructions
                print("-> dishtypes")
                yield from dts

        # all_items = [optalim, optalim_meta_planning, optalim_main_profile] + recipes + ingredients + instructions + dts

        JSONSerializer = serializers.get_serializer("json")
        json_serializer = JSONSerializer()

        with open("recipes_dump_%s.json" % timezone.now().strftime("%Y-%m-%d-%H%M%S"), "w") as f:
            json_serializer.serialize(AllItemsIterator(), stream=f)