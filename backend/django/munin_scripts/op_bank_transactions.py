#!/usr/bin/env python
from collections        import defaultdict
from bases.op_base      import DjangoMuninScript
from paybox.models      import Transaction

class TransactionDetails(DjangoMuninScript):
    STATUSES = {
        0: ("started", "AAAAAA"),
        1: ("cancelled", "d56de8"),
        2: ("refused", "ef7a13"),
        3: ("error", "ef1313"),
        4: ("post_cancel", "c40a0a"),
        5: ("wrong_amount", "8c0707"),
        10: ("accepted", "1aa659"),
        11: ("confirmed", "00ff00")
    }

    def apply_config(self):
        print("graph_title Bank transactions in the last 7 days")
        print('graph_category subscriptions')

        for i, status_data in enumerate(self.STATUSES.values()):
            key, color = status_data

            print("%s.draw %s" % (key, "AREA" if i ==0 else "STACK"))
            print("%s.label %s" % (key, key))
            print("%s.colour %s" % (key, color))


    def apply_values(self):
        transactions = Transaction.objects.filter(created_at__gte=self.ONE_WEEK_AGO)

        nb_per_status = defaultdict(int)
        for t in transactions:
            nb_per_status[t.status] += 1

        for i_status, status_data in self.STATUSES.items():
            key, color = status_data
            print("%s.value %i" % (key, nb_per_status[i_status]))

        for i_status, value in nb_per_status.items():
            if i_status not in self.STATUSES:
                print("unknown_%i.value %i" % (i_status, value))

TransactionDetails().apply()

