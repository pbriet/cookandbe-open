"""
This file runs the darwin algorithm with all the combinations
of nutrients (1 and 2).
It calculated the average time to get a solution, and the average cost if non-null.

It then stores everything into CSV files
"""
from hippocrate.benchmark.base  import HippocrateBenchmark
from optalim.config             import Config
from optalim.main               import OptalimWebsite
from mock                       import patch
import sys
import csv
import copy

# Number of times a configuration is tested (to minimize randomness)
SOLVE_SAMPLING = 10

# Running combinations of 1 and 2 nutrients
MAX_COMBINATION_LEVEL = 2

# Loading specific conf for darwin
OptalimWebsite.load_darwin_config('darwin_anc_benchmark.yml')


class DarwinAncBenchmark(HippocrateBenchmark):
    def setUp(self):
        # Creates everything in the DB
        HippocrateBenchmark.setUp(self)
        # Stores the list of ANC constraints as detailed in the anc.yml file
        self.all_constraints = Config.anc['adult_man']['nutrients']

    def get_constraint_combis(self, n):
        """
        Generates all combinations of N constraints
        """
        res = [ (copy.copy(c),) for c in self.all_constraints ]
        for i in range(n - 1):
            new_res = []
            for r in res:
                for constraint in self.all_constraints:
                    if constraint in r or constraint['name'] < r[-1]['name']:
                        continue
                    new_res.append(r + (constraint,))
            res = new_res
        return res

    def write_to_csv(self, depth, time_per_combi, cost_per_combi):
        """
        For one given depth, and time/cost per combination of constraints,
        dump everything in a CSV file
        """
        # First sort combinations per time descending
        time_per_combi = sorted(time_per_combi.items(), key=lambda x: x[1], reverse=True)

        # Write into file
        with open("anc_level_%i.csv" % (depth), "w") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(["constraint"] * depth + ["time", "score"])

            for constraint_combi_names, time_value in time_per_combi:
                row = list(constraint_combi_names)
                row.append(time_value)
                row.append(cost_per_combi[constraint_combi_names])
                csv_writer.writerow(row)

    def test_anc(self):
        partial_anc = copy.deepcopy(Config.anc)
        for depth in range(1, MAX_COMBINATION_LEVEL + 1):
            time_per_combi = {} # How much time is required to generate a potential perfect planning
            cost_per_combi = {} # If not perfect, which was the average cost

            # List of combinations
            combis = self.get_constraint_combis(depth)
            for i_comb, constraint_combi in enumerate(combis):
                
                constraint_combi_names = tuple(c['name'] for c in constraint_combi)
                # Replace all the constraints by only this combination
                partial_anc['adult_man']['nutrients'] = constraint_combi
       
                with patch.object(Config, 'anc', partial_anc):
                    # Run algorithm and stores time/cost
                    avg_cost, avg_time = self._run_algorithm("darwin", SOLVE_SAMPLING)
                    time_per_combi[constraint_combi_names] = avg_time
                    cost_per_combi[constraint_combi_names] = avg_cost
                    
                if (i_comb + 1) % 10 == 0:
                    print("%i / %i" % (i_comb + 1, len(combis)), file=sys.stderr)
              
            # Dump to CSV
            self.write_to_csv(depth, time_per_combi, cost_per_combi)

        self.assertTrue(True)
        
