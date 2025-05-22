
from django.core.management                 import call_command
from ext_tests.management.commands.optest   import Command as OpTestCommand

class Command(OpTestCommand):
    help = 'Run all tests files like application/tests/test_*.py (usefull in Windows environments with bad VM rights)'
    
    def handle(self, *args, **options):
        print("DEPRECATED: user ./manage.py optest --windows")
        options["windows"] = True
        super().handle(*args, **options)
