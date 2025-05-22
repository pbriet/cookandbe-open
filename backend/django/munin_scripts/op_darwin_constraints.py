#!/usr/bin/env python
from bases.op_base      import DjangoMuninScript
from optalim.mongo      import Mongo

class DarwinConstraintsFilters(DjangoMuninScript):

    def apply_config(self):
        print("graph_title Darwin constraints and filters (last week)")
        print('graph_category darwin')
        print("constraints.draw LINE1")
        print("constraints.colour 000000")
        print("constraints.label Nombre de contraintes (moyenne)")
        print("filters.draw LINE1")
        print("filters.colour 777777")
        print("filters.label Nombre de filtres (moyenne)")
        print("broken.draw LINE1")
        print("broken.colour AA0000")
        print("broken.label Nombre de contraintes enfreintes (moyenne)")

    def apply_values(self):

        group_by = {'nb_constraints':{'$avg':'$nb_constraints'},
                    'nb_filters':{'$avg':'$nb_filters'},
                    'nb_broken_constraints':{'$avg':'$nb_broken_constraints'}}

        aggregate_user = {'_id': '$user_id'}
        aggregate_user.update(group_by)

        aggregate_all = {'_id': None}
        aggregate_all.update(group_by)

        table = Mongo.log_table('darwin_quality')
        query = [{'$match': {'date' : {'$gte': self.ONE_WEEK_AGO}}},
                 {'$group': aggregate_user}, # Group by user first
                 {'$group': aggregate_all}]  # Then all users

        res = list(table.aggregate(query))
        if len(res) == 0:
            print("constraints.value 0")
            print("filters.value 0")
            print("broken.value 0")
        else:
            res = res[0]
            print("constraints.value %s" % res['nb_constraints'])
            print("filters.value %s" % res['nb_filters'])
            print("broken.value %s" % res['nb_broken_constraints'])

DarwinConstraintsFilters().apply()