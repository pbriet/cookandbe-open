from django.core.management.base import BaseCommand, CommandError
from nutrient.models             import FoodNutrient
from recipe_mgr.models           import Recipe, RecipeDishType,\
                                        FoodTag, FoodTagSet, FoodType, FoodConversion
from django.core.serializers     import serialize
from optparse                    import make_option
from collections                 import defaultdict
import sys

class Command(BaseCommand):
    args = '[--nutrients | -n] [--nutrient-ids=<nutrient_id>,<nutrient_id> ...]  <recipe_id recipe_id ...>'
    help = 'Dump in stdout a JSON fixture containing a Recipe and its dependencies'

    option_list = BaseCommand.option_list + (
            make_option('--nutrients', '-n',
                action='store_true', dest='nutrients',
                default=False,
                help='Dump nutrients and nutrient values too'),
            make_option('--nutrient-ids', '-i',
                        action='store', dest='nutrients_ids',
                        default=None,
                        help='Dump a specific list of nutrients')
            )


    def handle(self, *args, **options):
        if options.get('nutrients_ids', None):
            options['nutrients_ids'] = [int(i) for i in options['nutrients_ids'].split(',')]
        recipes = []
        for recipe_id in args:
            try:
                recipes.append(Recipe.objects.get(pk=recipe_id))
            except Recipe.DoesNotExist:
                raise CommandError('Recipe "%s" does not exist"' % recipe_id)

        objects = []

        def add(o):
            if o not in objects:
                objects.append(o)

        for recipe in recipes:
            add(recipe)
            add(recipe.author)
            for r_dish_type in RecipeDishType.objects.filter(recipe=recipe):
                add(r_dish_type)
                add(r_dish_type.dish_type)
            for ingredient in recipe.ingredients.all():
                add(ingredient)
                add(ingredient.food)
                add(ingredient.cooking_method)
                add(ingredient.raw_state)
                add(ingredient.food.food_source)
                add(ingredient.food.type)
                for fg in FoodTagSet.objects.filter(food=ingredient.food):
                    add(fg)
                    add(fg.tag)
                    add(fg.component)
                if options.get('nutrients', None) or options.get('nutrients_ids', None):
                    for fn in FoodNutrient.objects.filter(food=ingredient.food):
                        if options.get('nutrients_ids', None) and fn.nutrient_id not in options['nutrients_ids']:
                            continue
                        add(fn)
                        add(fn.nutrient)
                        add(fn.cooking_method)
                        add(fn.raw_state)
                for fc in FoodConversion.objects.filter(food=ingredient.food):
                    add(fc)


        sys.stdout.write(serialize('json', [o for o in reversed(objects)],
                indent=4))
