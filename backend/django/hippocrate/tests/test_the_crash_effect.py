"""
Testing how meal time limit is constraining recipes
"""
from hippocrate.tests                       import DefaultMetaPlanningHippocrateTest
from mock                                   import patch
from common.mock_tools                      import empty_diet_decorator, fake_today_decorator
import hippocrate.models.problem
import datetime

class CrashEffectException(Exception):
    def __str__(self):
        return "Oh Oh"

def oh_oh(*args, **kargs):
    raise CrashEffectException()

class TestTheCrashEffect(DefaultMetaPlanningHippocrateTest):
    """
    Test that the database is not affected when a crash occurs
    """
        
    @patch.object(hippocrate.models.problem.Problem, 'solve_darwin', oh_oh)
    def test_crash(self):
        self.assertEqual(self._nb_days(), 7) # Metaplanning
        self.assertEqual(self._nb_dishrecipes(), 21)
        
        # Planning fill, and suggest API
        for fcn in (self._fill_through_api, self._suggest_through_api):
            self.assertRaises(CrashEffectException, fcn)
            
            self.assertEqual(self._nb_days(), 7) # Metaplanning-only
            self.assertEqual(self._nb_dishrecipes(), 21)
        
    
    def _test_success(self, fcn):
        """
        Test with no crash, to ensure that the non-patched version is working correctly  (not an other AssertionError)
        """
        self.assertEqual(self._nb_days(), 7) # Metaplanning
        self.assertEqual(self._nb_dishrecipes(), 21)
        fcn()
        self.assertEqual(self._nb_days(), 14) # Metaplanning + planning
        self.assertTrue(self._nb_dishrecipes() > 50)
    
    def test_fill_success(self):
        self._test_success(self._fill_through_api)
    
    def test_suggest_success(self):
        self._test_success(self._suggest_through_api)
        
    @empty_diet_decorator
    @fake_today_decorator(2014, 1, 27)
    def _fill_through_api(self):
        date = datetime.date(2014, 1, 28)
        super()._fill_through_api(date)
        
    @empty_diet_decorator
    @fake_today_decorator(2014, 1, 27)
    def _suggest_through_api(self):
        date = datetime.date(2014, 1, 28)
        super()._suggest_through_api(date)
        