
from common.math            import round_to_closest
from common.test            import OptalimTest


class TestRoundToClosest(OptalimTest):
    
    def test_round_to_closest(self):
        
        self.assertEqual(round_to_closest(94, 10), 90)
        self.assertEqual(round_to_closest(96, 10), 100)
        self.assertEqual(round_to_closest(1.6, 0.5), 1.5)
        self.assertEqual(round_to_closest(1.8, 0.5), 2)
        self.assertEqual(round_to_closest(1.5, 0.5), 1.5)
        self.assertAlmostEqual(round_to_closest(0.33333, 0.1), 0.3, 1)