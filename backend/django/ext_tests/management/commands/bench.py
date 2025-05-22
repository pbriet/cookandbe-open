from django.core.management             import call_command
from django.core.management.base        import BaseCommand

class Command(BaseCommand):
    args = ''
    help = 'Start a benchmark file'

    def handle(self, *args, **options):
        args = args + ('--nologcapture',)
        call_command('test', *args, **options)