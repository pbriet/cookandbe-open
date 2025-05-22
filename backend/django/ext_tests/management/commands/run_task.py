from django.core.management.base        import BaseCommand
import importlib

class Command(BaseCommand):
    help = 'Test a task  ./manage.py run_task planning_mgr.tasks.delete_old_plannings'

    def add_arguments(self, parser):
        parser.add_argument('path', nargs=1, type=str)
        parser.add_argument('task_args', nargs='*', type=str)
        
    def handle(self, **options):
        
        arg = options['path'][0]
        splitted = arg.split(".")
        
        module_name = ".".join(splitted[:-1])
        fcn_name = splitted[-1]
        
        module = importlib.import_module(module_name)
        fcn = getattr(module, fcn_name)
        
        fcn(*(options.get('task_args', [])))