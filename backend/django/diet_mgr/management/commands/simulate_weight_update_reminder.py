from django.core.management.base import BaseCommand
from diet_mgr.tasks              import remind_weight_update
from optalim.settings            import DEBUG

class Command(BaseCommand):
    args = ''
    help = 'Simulate the weight reminder task'

    def handle(self, *args, **options):
        if not DEBUG:
            raise RuntimeError("DEBUG mode not activated : will send email. Aborting")
        remind_weight_update(simulate=True)