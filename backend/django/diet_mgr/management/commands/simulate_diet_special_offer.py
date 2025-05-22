from django.core.management.base import BaseCommand
from diet_mgr.tasks              import auto_diet_special_offer
from optalim.settings            import DEBUG

class Command(BaseCommand):
    args = ''
    help = 'Simulate the special offers'

    def handle(self, *args, **options):
        if not DEBUG:
            raise RuntimeError("DEBUG mode not activated : will send email. Aborting")
        auto_diet_special_offer(simulate=True)