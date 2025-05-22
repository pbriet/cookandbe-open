from django.core.management.base    import BaseCommand
from recipe_mgr.tasks               import update_recipe_ratings

class Command(BaseCommand):
    args = ''
    help = 'Update the recipe ratings'

    def handle(self, *args, **options):
        update_recipe_ratings()