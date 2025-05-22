#!/usr/bin/env python
from collections        import defaultdict
from op_base            import DjangoMuninScript
from optalim.mongo      import Mongo

class BaseDarwinQuality(DjangoMuninScript):

    CATEGORY_SIZE = 200
    NB_CATEGORIES = 5  # + 1 which is "more_than_max"
    SCORE_TYPE = None
    TITLE = None

    def __init__(self):
        super().__init__()
        self.keys = []
        for i in range(self.NB_CATEGORIES):
            self.keys.append("from_%i_to_%i" % (i * self.CATEGORY_SIZE, (i + 1) * self.CATEGORY_SIZE))
        self.keys.append("more_than_%i" % (self.CATEGORY_SIZE * self.NB_CATEGORIES))

    def apply_config(self):
        print("graph_title %s" % self.TITLE)
        print('graph_category darwin')
        print('graph_args --lower-limit 0')
        for i, key in enumerate(self.keys):
            print("%s.draw %s" % (key, "AREA" if i == 0 else "STACK"))
            if i < self.NB_CATEGORIES:
                print("%s.label %i < cost < %i" % (key, i*self.CATEGORY_SIZE, (i + 1) * self.CATEGORY_SIZE))
            else:
                print("%s.label cost > %i" % (key, i*self.CATEGORY_SIZE))


    def apply_values(self):
        table = Mongo.log_table('darwin_quality')
        self.values = table.aggregate([
                            {'$match': {'date' : {'$gte': self.ONE_WEEK_AGO}}},
                            {'$group': {'_id': '$user_id', self.SCORE_TYPE: {'$avg': '$%s' % self.SCORE_TYPE}}}
                                     ])

        self.values = [row[self.SCORE_TYPE] for row in self.values]

        stats = defaultdict(int)
        for value in self.values:
            i_category = value // self.CATEGORY_SIZE
            if i_category > self.NB_CATEGORIES:
                i_category = self.NB_CATEGORIES
            stats[i_category] += 1

        nb_logs = len(self.values)
        if nb_logs == 0:
            return

        for i, key in enumerate(self.keys):
            print("%s.value %s" % (key, float(100 * stats.get(i, 0)) / nb_logs))
