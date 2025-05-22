from django.core.management.base import BaseCommand, CommandError
from nutrient.models             import FoodNutrient
from recipe_mgr.models           import Food, FoodConversion, FoodTagSet,\
                                        FoodSeasonality
import copy

class Command(BaseCommand):
    args = 'food_id cloned_food_name'
    help = 'Create a deep copy of a food in the database, with a new food name. The new food created will be child of the original one'

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError('Invalid number of arguments (expected: 2)')
        try:
            food_id = int(args[0])
        except ValueError:
            raise CommandError('First argument is not an id')

        new_food_name = args[1]
        
        food = Food.objects.get(pk=food_id)
        new_food = copy.copy(food)
        new_food.id = None # Force the database to consider this is a new object
        new_food.name = new_food_name
        new_food.full_name = new_food_name
        new_food.parent = food
        new_food.type = food.type
        new_food.save()

        for cls in (FoodNutrient, FoodConversion, FoodTagSet, FoodSeasonality):
            for obj in cls.objects.filter(food_id=food.id):
                new_obj = copy.copy(obj)
                new_obj.id = None
                new_obj.food_id = new_food.id
                new_obj.save()

        print("Food %s is now a clone of %s" % (new_food_name, food.name))