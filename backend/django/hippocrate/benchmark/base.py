"""
Base class for a benchmark that runs on the current recipe database
with a default planning.
"""
from common.test                import TestAPIWithLogin
from hippocrate.models.database import DishType, DishTypeAggregation, Nutrient
from planning_mgr.models        import Planning, MealDishOption, MealType
from hippocrate.models.problem  import Problem
from optalim.main               import OptalimWebsite
import time
import numpy

# Loading recipes from prod DB
OptalimWebsite.load_recipes(threaded=False)
# Loading darwin configuration
OptalimWebsite.load_darwin_config('darwin.yml')

# Retrieving objects from production DB
COPY_FROM_DB_CLS = [DishType, DishTypeAggregation, Nutrient, MealDishOption, MealType]
prod_objects = []
for cls in COPY_FROM_DB_CLS:
    prod_objects.extend(cls.objects.all())

class HippocrateBenchmark(TestAPIWithLogin):
    def setUp(self):
        TestAPIWithLogin.setUp(self)
        
        # Creating profile and eater
        self.init_db_profile_eater()

        # Copying prod objects into isolated test DB
        for o in prod_objects:
            o.save()

        # Creating default planning and "next week's planning"
        response = self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/api/user/%i/planning/next_week/init' % self.user.id)
        self.assertEqual(response.status_code, 201)

    def _run_algorithm(self, algorithm, run_x_times=1):
        """
        With the given configuration, runs X times the algorithm and calculates
        average cost/time
        """
        planning = list(Planning.objects.all())[0]
        problem = Problem(planning)
        scores = []
        times = []
        for i in range(run_x_times):
            t = time.time()
            solution = getattr(problem, "solve_" + algorithm)()
            times.append(time.time() - t)
            scores.append(problem.eval(solution).total)

        return round(numpy.mean(scores), 2), round(numpy.mean(times), 5)
