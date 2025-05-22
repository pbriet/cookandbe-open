#!/usr/bin/env python
import sys, os

os.environ['DJANGO_SETTINGS_MODULE'] = 'optalim.settings'

from django.conf        import settings
from django.utils       import timezone
import datetime

settings.LOGGING = None

import django
django.setup()

class DjangoMuninScript(object):
    """
    Munin script that runs within a django environment
    """
    ONE_DAY_AGO   = timezone.now() - datetime.timedelta(days=1)
    TWO_DAYS_AGO  = timezone.now() - datetime.timedelta(days=2)
    ONE_WEEK_AGO  = timezone.now() - datetime.timedelta(days=7)
    TEN_DAYS_AGO  = timezone.now() - datetime.timedelta(days=10)
    TWO_WEEKS_AGO = timezone.now() - datetime.timedelta(days=14)
    ONE_MONTH_AGO = timezone.now() - datetime.timedelta(days=30)

    def apply_autoconf(self):
        print("yes")

    def apply_config(self):
        """
        Returns the configuration of munin script.
        Example :
        print("graph_title Some title for our plugin2")
        print("something.label Foobar per second")
        """
        raise NotImplementedError

    def apply_config(self):
        """
        Returns the values
        Example :
        print("something.value 42")
        """
        raise NotImplementedError

    def apply(self):
        if len(sys.argv) > 1 and sys.argv[1] == "autoconf":
            return self.apply_autoconf()
        if len(sys.argv) > 1 and sys.argv[1] == "config":
            return self.apply_config()
        return self.apply_values()