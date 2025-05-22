"""
This file runs the darwin algorithm multiple times, and returns :
* The Average, min, max, and stddev  score
* Same for time
"""
from hippocrate.benchmark.base  import HippocrateBenchmark
import sys
import numpy

NB_ALGORITHM_RUN = 50

class DarwinAncBenchmark(HippocrateBenchmark):

    def test_bench_darwin(self):

        costs = []
        times = []
        for i in range(NB_ALGORITHM_RUN):
           avg_cost, avg_time = self._run_algorithm("darwin")
           print("run %i = %ss (cost = %s)" % (i, round(avg_time, 2), avg_cost), file=sys.stderr)
           costs.append(avg_cost)
           times.append(avg_time)

        print("", file=sys.stderr)
        print("* COST = ", round(numpy.mean(costs)), file=sys.stderr)
        print(" > MIN/MAX = ", numpy.min(costs), " | ", numpy.max(costs), file=sys.stderr)
        print(" > STD-DEV = ", round(numpy.std(costs)), file=sys.stderr)

        print("", sys.stderr)
        print("* TIME = ", round(numpy.mean(times), 2), file=sys.stderr)
        print(" > MIN/MAX = ", round(numpy.min(times), 2), " | ", round(numpy.max(times), 2), file=sys.stderr)
        print(" > STD-DEV = ", round(numpy.std(times), 2), file=sys.stderr)
        self.assertTrue(True)
