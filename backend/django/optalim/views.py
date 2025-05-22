
from django.http                    import HttpResponse
from django.utils                   import timezone

from common.date                    import make_utc

from optalim.settings               import DJANGO_PATH

import os
import datetime

def is_alive(request):
    return HttpResponse("Still cooking delicious meals at %s" % timezone.now().strftime("%Y-%m-%d %H:%M:%S"))

def celery_is_alive(request):
    celery_last_exec_filepath = os.path.join(DJANGO_PATH, "celery-last.log")
    with open(celery_last_exec_filepath) as f:
        datetime_str = f.read()
        last_exec = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        last_exec = make_utc(last_exec)

    time_elapsed = (timezone.now() - last_exec).seconds

    if time_elapsed < 1800:
        http_code = 200
    else:
        http_code = 404

    return HttpResponse("Last celery beat %i seconds ago" % time_elapsed, status=http_code)
