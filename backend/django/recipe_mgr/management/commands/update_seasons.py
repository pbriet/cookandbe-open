from django.core.management.base    import BaseCommand
from recipe_mgr.seasons             import SeasonManager

class Command(BaseCommand):
    args = ''
    help = 'Update the cache of recipe seasonality'

    def handle(self, *args, **options):
        SeasonManager.update_all()