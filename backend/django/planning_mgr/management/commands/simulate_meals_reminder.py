from django.core.management.base import BaseCommand

from planning_mgr.tasks          import send_meals_reminder
from optalim.settings            import DEBUG

import diet_mgr.import_all

class Command(BaseCommand):
    args = ''
    help = 'Simulate the sending of daily reminder emails'

    def handle(self, *args, **options):
        if not DEBUG:
            raise RuntimeError("DEBUG mode not activated : will send email. Aborting")
        send_meals_reminder(simulate=True)