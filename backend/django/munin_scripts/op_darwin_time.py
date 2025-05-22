#!/usr/bin/env python
from bases.op_base      import DjangoMuninScript
from optalim.mongo      import Mongo

class DarwinTime(DjangoMuninScript):
    def apply_config(self):
        print("graph_title Darwin execution time (last week)")
        print('graph_category darwin')
        print("full_execution.draw LINE1")
        print("full_execution.label Full planning generation")
        print("all.draw LINE1")
        print("all.label Any optimization call")


    def apply_values(self):
        table = Mongo.log_table('darwin_times')

        # Aggregation
        group_query = {'_id': None, 'AverageTime':{'$avg':'$values.solve.real'}}

        # Filtering only full generations
        query = [{'$match': {'date' : {'$gte': self.ONE_WEEK_AGO},
                             'context.start_from_existing_solution' : False,
                             'context.some_dish_ids_only' : False}},
                 {'$group': group_query}]

        res = table.aggregate(query)
        res = list(res)
        if len(res) == 0:
            return
        print("full_execution.value %f" % res[0]['AverageTime'])

        # No filter at all
        query = [{'$match': {'date' : {'$gte': self.ONE_WEEK_AGO}}},
                 {'$group': group_query}]
        res = table.aggregate(query)
        res = list(res)
        print("all.value %f" % res[0]['AverageTime'])


DarwinTime().apply()
