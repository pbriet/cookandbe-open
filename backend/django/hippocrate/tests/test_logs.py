from common.mock_tools              import fake_mongo_decorator

from hippocrate.controls.logs       import save_darwin_finished_logs, save_constraint_logs, save_darwin_started_log
from hippocrate.models.constraints  import UnicityConstraint
from hippocrate.tests               import HpUnidishApiTest

from mock                           import patch

import datetime
import diet_mgr.handlers.anc
import hippocrate.controls.logs
import hippocrate.models.problem

class HippocrateLogsTest(HpUnidishApiTest):
    """
    Test that hippocrate logs correctly data into mongo
    """
    # Unable to avoid redudancy : solution will have some cost
    NB_RECIPES          = 1
    NB_MEALSLOTS        = 2
    NB_SLOTS_PER_DAY    = 2
    NB_DISHES_PER_MEAL  = 1
    
    def init_problem(self, forced_constraints=None, **kargs):
        return super().init_problem(forced_constraints=[UnicityConstraint(300, [self.defaultDishType.id])], **kargs)
    
    @fake_mongo_decorator
    @patch.object(hippocrate.controls.logs, 'ENABLE_MONGO_TESTING', True)
    @patch.object(hippocrate.models.problem, 'ENABLE_MONGO_TESTING', True)
    def test_logs(self, mock_mongo_tables):
        save_darwin_started_log(self.problem)
        solution = self.problem.solve_darwin()
        save_darwin_finished_logs(self.problem)
        score = self.problem.eval(solution)
        save_constraint_logs(self.problem, solution, score)
        
        # Checking the performance log
        darwin_time_logs = mock_mongo_tables['darwin_times'].written_data
        self.assertEqual(len(darwin_time_logs), 1)
        entry = darwin_time_logs[0]
        self.assertEqual(sorted(entry.keys()), ['context', 'date', 'problem_key', 'user_id', 'values'])
        self.assertEqual(entry['user_id'], self.user.id)
            
        # Checking the quality log
        darwin_quality_logs = mock_mongo_tables['darwin_quality'].written_data
        self.assertEqual(len(darwin_quality_logs), 1)
        entry = darwin_quality_logs[0]
        self.assertEqual(entry['user_id'], self.user.id)
        self.assertEqual(entry['nb_filters'], 1) # Max budget
        self.assertEqual(entry['total_score'], 300)
        self.assertEqual(entry['broken_constraints'], [('unicity', 300)])

        # Checking the crash detection log
        darwin_crash_logs = mock_mongo_tables['crash_check'].written_data
        self.assertEqual(len(darwin_crash_logs), 2)
        self.assertEqual(darwin_crash_logs[0]['status'], 'start')
        self.assertEqual(darwin_crash_logs[1]['status'], 'end')
        self.assertEqual(darwin_crash_logs[0]['problem_key'], darwin_crash_logs[1]['problem_key'])