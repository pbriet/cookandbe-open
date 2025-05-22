#ifndef ALGORITHM_DARWIN_OPERATOR_H_
# define ALGORITHM_DARWIN_OPERATOR_H_

# include "hippocrate/controls/algorithm/darwin/types.h"

class DarwinAlgorithm;

/*
 * Represents a weakness in one solution :
 * - a broken constraint
 * - a specific dish
 */
class Weakness
{
public:
  Weakness(const Rule * r, long _dish_id) : rule(r), dish_id(_dish_id) {};
                      
  const Rule * rule;
  long dish_id;
};

class GeneticOperator
{
public:
  explicit          GeneticOperator(DarwinAlgorithm * algorithm) : algorithm(algorithm) {}
  virtual           ~GeneticOperator() {}

protected:
  DarwinAlgorithm   * algorithm;

  Weakness                    find_weakness(const Solution * individual);
  const Rule *   pick_highest_constraint(const Solution * individual, bool filter_large_constraints=false) const;
  const Rule *   pick_proportional_constraint(const Solution * individual, bool filter_large_constraints=false) const;
};

#endif