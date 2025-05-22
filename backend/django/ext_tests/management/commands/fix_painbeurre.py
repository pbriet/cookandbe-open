from django.core.management.base        import BaseCommand
from django.core.cache import cache

from recipe_mgr.models import Recipe, DishType
from planning_mgr.models import DishRecipe

class Command(BaseCommand):
    args = ''
    help = 'Replace "Pain beurre chocolat" by "Orange" in recent plannings'

    def handle(self, *args, **options):

        r = Recipe.objects.get(name="Pain beurre chocolat")
        orange = Recipe.objects.get(name="Orange")

        dessert = DishType.objects.get(name=DishType.DT_DESSERT)

        DishRecipe.objects.filter(pk__gt=11000000, recipe=r, dish__dish_type=dessert).update(recipe=orange)
