from celery import shared_task

from optalim.settings           import DJANGO_PATH

from django.utils               import timezone

import os


@shared_task
def celery_alive():
    """
    Store the last time this task was run, to ensure that Celery is alive
    """
    celery_last_exec_filepath = os.path.join(DJANGO_PATH, "celery-last.log")
    with open(celery_last_exec_filepath, "w") as f:
        f.write(timezone.now().strftime("%Y-%m-%d %H:%M:%S"))
