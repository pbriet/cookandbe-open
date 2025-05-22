#!/usr/bin/env python
from collections        import defaultdict
from bases.op_base      import DjangoMuninScript
from optalim.mongo      import Mongo
import numpy

class DarwinBrokenConstraints(DjangoMuninScript):
    def __init__(self):
        super().__init__()
        table = Mongo.log_table('darwin_quality')
        self.values = defaultdict(list)
        nb_total = 0

        for row in table.find({'date' : {'$gte': self.ONE_WEEK_AGO}}, {'broken_constraints': 1}):
            nb_total += 1
            for constraint in row["broken_constraints"]:
                if constraint[0] == 'unicity':
                    continue
                self.values[constraint[0]].append(constraint[1])

        for key in self.values.keys():
            nb_zeros = nb_total - len(self.values[key])
            self.values[key] = [0] * nb_zeros + sorted(self.values[key])


    def apply_config(self):
        print("graph_title Darwin average constraint score (last week - 98% lowest scores)")
        print('graph_category darwin')
        print('graph_info Warning: not normalized per user')
        print('graph_args --lower-limit 0')
        for key in self.values.keys():
            print("%s.draw LINE1" % key)
            print("%s.label %s" % (key, key))

    def apply_values(self):
        for key, values in self.values.items():
            # Removing extreme value
            max_value = numpy.percentile(values, 95)
            i_max = max(1, numpy.searchsorted(values, max_value))
            values = values[:i_max]
            print("%s.value %s" % (key, numpy.mean(values)))

DarwinBrokenConstraints().apply()