from django.core.management.base import BaseCommand
from recipe_mgr.controller       import RecipeImageGenerator
from recipe_mgr.models           import Recipe
"""
This scripts automatically generates recipe images from their food_tags, only
if there aren't already an uploaded image
"""

class Command(BaseCommand):
    args = ''
    help = 'Generates/updates images for recipes with auto-images'

    def handle(self, *args, **options):
        for recipe in Recipe.objects.filter(status__gte=Recipe.STATUS_PUBLISHED):
            if recipe.auto_photo:
                print("* ", recipe.name)
                RecipeImageGenerator(recipe.id)()