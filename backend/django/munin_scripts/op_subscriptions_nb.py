#!/usr/bin/env python
from bases.op_base      import DjangoMuninScript
from paybox.models      import Subscription

from common.date        import today
from datetime           import timedelta

class NbActiveSubscriptions(DjangoMuninScript):
    def apply_config(self):
        print("graph_title Number of subscriptions (non-free)")
        print('graph_category subscriptions')
        print("active.draw LINE1")
        print("active.label currently active")

    def apply_values(self):
        subscriptions = Subscription.objects.filter(start_date__lte = today(), end_date__gte = today(),
                                                    total_amount__gt=0,
                                                    cancelled = False, enabled = True)
        nb_active = subscriptions.count()

        print("active.value %i" % nb_active)


NbActiveSubscriptions().apply()