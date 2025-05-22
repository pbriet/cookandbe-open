#ifndef ALGORITHM_DARWIN_H_
# define ALGORITHM_DARWIN_H_

# include <list>
# include "hippocrate/controls/algorithm/algorithm.h"
# include "hippocrate/controls/algorithm/darwin/config.h"
# include "hippocrate/controls/algorithm/darwin/types.h"
# include "hippocrate/controls/algorithm/darwin/crossovers/crossover.h"
# include "hippocrate/controls/algorithm/darwin/mutations/mutation.h"

class DarwinAlgorithm : public Algorithm
{
public:
  explicit                      DarwinAlgorithm(Problem *p);
  virtual                       ~DarwinAlgorithm();
  virtual Solution              solve() override final;

  // Current population
  hp::darwin::Population        population;
  // New born individuals
  std::list<Solution *>         children;
  // Scores (lazy)
  hp::darwin::PopulationScores  scores;
  // Constraints list
  hp::darwin::ConstraintsDict   mutable_constraints;

  Crossover *                   random_crossover;
  Crossover *                   oriented_crossover;
  Mutation *                    random_mutation;
  Mutation *                    oriented_mutation;

protected:
  void                          compute_population_variation() const;

private:
  void                          init_constraints();
  void                          init_population();
  bool                          should_continue();
  void                          cross();
  void                          mutate();
  void                          add_children();
  void                          evaluate();
  void                          select();
  void                          check_validity_before_start() const;
  
  long                          generation_no = 0;
  double                        oriented_cross_rate = 0;
  double                        oriented_mutation_rate = 0;
  long                          last_best_score = -1;
  uint                          nb_lost_generations = 0;  // Number of generations without improvement
};

#endif