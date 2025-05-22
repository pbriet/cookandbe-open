from django.core.management.base        import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType
from django.db.utils                    import DatabaseError
import sys

class Command(BaseCommand):
    args = ''
    help = 'Flush all tables except the one managed by South'

    def handle(self, *args, **options):

        for ct in ContentType.objects.all():
            try:
                if not "south." in str(ct.model_class()):
                    ct.model_class().objects.all().delete()
            except DatabaseError:
                print("Warning: unable to clear data for class %s" % ct.model_class().__name__, file=sys.stderr)