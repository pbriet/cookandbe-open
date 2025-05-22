from django.core.management.base        import BaseCommand
from django.core.cache import cache

class Command(BaseCommand):
    args = ''
    help = 'Clear the cache (entirely)'

    def handle(self, *args, **options):
        print("Clearing...")
        cache.clear()
        print("DONE")