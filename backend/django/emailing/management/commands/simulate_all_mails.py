
from django.core.management.base    import BaseCommand

from emailing.tools                 import sendmail_template, MessageType

from optalim.settings               import DEBUG, DJANGO_PATH

from user_mgr.models                import User

from collections                    import defaultdict

import os

class Command(BaseCommand):
    args = ''
    help = 'Send one email of each type'

    def handle(self, *args, **options):
        # Security
        if not DEBUG:
            raise RuntimeError("DEBUG mode not activated : will send email. Aborting")
        # Default
        user = User.objects.get(id = 4)
        # Templates
        templates = []
        for app_dir in os.listdir(DJANGO_PATH):
            template_dir = os.path.join(DJANGO_PATH, app_dir, "templates")
            if os.path.isdir(template_dir):
                for template_file in os.listdir(template_dir):
                    if template_file.endswith(".html"):
                        templates.append(os.path.join(app_dir, "templates", template_file))
        # Sending
        for template_path in templates:
            print(template_path)
            object = template_path.split('/')[-1][:-5]
            variables = dict()
            sendmail_template(MessageType.NOTIFICATION, template_path, variables, object, users=[user], send_async=False)
