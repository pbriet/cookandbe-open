from django.core.management.base import BaseCommand
from diet_mgr.tasks              import update_metabolisms
from optalim.settings            import DEBUG

class Command(BaseCommand):
    args = ''
    help = 'Calls the metabolism update task (usually called every day)'

    def handle(self, *args, **options):
        if not DEBUG:
            raise RuntimeError("DEBUG mode not activated : will send email. Aborting")
        update_metabolisms()