#ifndef ALGORITHM_DARWIN_CROSSOVERS_CROSSOVER_H_
# define ALGORITHM_DARWIN_CROSSOVERS_CROSSOVER_H_

# include "hippocrate/controls/algorithm/darwin/operator.h"

class DarwinAlgorithm;

class Crossover : public GeneticOperator
{
public:
  explicit          Crossover(DarwinAlgorithm * algorithm) : GeneticOperator(algorithm) {}
  virtual           ~Crossover() {}

  // Mate parent1 with someone and returns the number of children
  virtual int       cross(const Solution * parent1) = 0;
  virtual const char *        type() const = 0;

protected:
  Solution *                  cross_a_to_b(const Solution * a, const Solution * b, const Rule * cross_constraint);
  int                         constraint_mating(const Solution * parent1, const Solution * parent2, const Rule * cross_constraint, bool one_way_only=false);
  const Solution *            pick_best_mate(const Solution * parent1, const Rule * constraint) const;
  const Solution *            pick_better_mate(const Solution * parent1, const Rule * constraint) const;
  
};

class RandomMateCrossover : public Crossover
{
public:
  explicit          RandomMateCrossover(DarwinAlgorithm * algorithm) : Crossover(algorithm) {}
  virtual           ~RandomMateCrossover() {}

  // Mate parent1 with someone and returns the number of children
  int               cross(const Solution * parent1);
  virtual const char *        type() const{ return "RandomMateCrossover"; };
};

class ProportionalConstraintRandomMateCrossover : public Crossover
{
public:
  explicit          ProportionalConstraintRandomMateCrossover(DarwinAlgorithm * algorithm) : Crossover(algorithm) {}
  virtual           ~ProportionalConstraintRandomMateCrossover() {}

  // Mate parent1 with someone and returns the number of children
  int               cross(const Solution * parent1);
  virtual const char *        type() const{ return "ProportionalConstraintRandomMateCrossover"; };
};

class ProportionalConstraintBetterMateCrossover : public Crossover
{
public:
  explicit          ProportionalConstraintBetterMateCrossover(DarwinAlgorithm * algorithm) : Crossover(algorithm) {}
  virtual           ~ProportionalConstraintBetterMateCrossover() {}

  // Mate parent1 with someone and returns the number of children
  int               cross(const Solution * parent1);
  virtual const char *        type() const{ return "ProportionalConstraintBetterMateCrossover"; };
};

class HighConstraintBestMateCrossover : public Crossover
{
public:
  explicit          HighConstraintBestMateCrossover(DarwinAlgorithm * algorithm) : Crossover(algorithm) {}
  virtual           ~HighConstraintBestMateCrossover() {}

  // Mate parent1 with someone and returns the number of children
  int               cross(const Solution * parent1);
  virtual const char *        type() const{ return "HighConstraintBestMateCrossover"; };
};

#endif