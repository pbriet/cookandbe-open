#!/usr/bin/env python
from collections        import defaultdict
from bases.op_base      import DjangoMuninScript

from diet_mgr.models    import Diet

from user_mgr.models    import User

class DietDistribution(DjangoMuninScript):
    def __init__(self):
        super().__init__()
        self.diets = list(Diet.objects.all().order_by('key'))
        self.diets_by_id = dict((d.id, d) for d in self.diets)

    def apply_config(self):
        print("graph_title Diet distribution")
        print('graph_category diets')
        print('graph_args --lower-limit 0')
        for i, diet in enumerate(self.diets):
            print("%s.draw %s" % (diet.key, "AREA" if i ==0 else "STACK"))
            print("%s.label %s" % (diet.key, diet.key))

    def apply_values(self):
        users = User.objects.filter(enabled=True).only('diet').all()

        diet_count = defaultdict(int)
        for user in users:
            diet_count[user.diet_id] += 1

        for diet_id, diet in self.diets_by_id.items():
            nb = diet_count.get(diet_id, 0)
            print("%s.value %i" % (diet.key, nb))


DietDistribution().apply()