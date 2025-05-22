from django.core.management.base    import BaseCommand
from collections                    import defaultdict
from recipe_mgr.models              import Recipe
from hippocrate.models.recipe       import RecipeDataBuilder

import numpy

class Command(BaseCommand):
    args = ''
    help = 'Calculated the avg and median calories per dishtype'

    def handle(self, *args, **options):
        
        calories_per_dishtype = defaultdict(list)
        
        calories_per_recipe_id = {}
        all_recipes = list(Recipe.objects.filter(internal=False, status=Recipe.STATUS_PUBLISHED).prefetch_related('dish_types'))
        recipe_by_id = dict((r.id, r) for r in all_recipes)
        all_recipe_ids = [r.id for r in all_recipes]
        all_recipe_data = RecipeDataBuilder().get_or_build_many(all_recipe_ids)
        
        for recipe_data in all_recipe_data:
            recipe = recipe_by_id[recipe_data.recipe_id]
            for dish_type in recipe.dish_types.all():
                recipe_calories = recipe_data.get_data_from_key("energiekilocalories", 1)
                calories_per_dishtype[dish_type.name].append(recipe_calories)
                
        
        for dish_type_name, values in sorted(calories_per_dishtype.items(), key=lambda x: x[0]):
            avg = round(numpy.mean(values))
            med = round(numpy.median(values))
            min_val = round(numpy.min(values))
            max_val = round(numpy.max(values))
            nb = len(values)
            
            print("%s [%i] :\t avg=%i\tmed=%i  ([%i-%i])" % (dish_type_name, nb, avg, med, min_val, max_val))
                