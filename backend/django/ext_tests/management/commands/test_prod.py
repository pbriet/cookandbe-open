
from django.core.management                 import call_command
from ext_tests.management.commands.optest   import Command as OpTestCommand

class Command(OpTestCommand):
    help = 'Test in a production-like environment (with PGSQL)'
    
    def handle(self, *args, **options):
        print("DEPRECATED: user ./manage.py optest --pgsql")
        options["pgsql"] = True
        super().handle(*args, **options)
