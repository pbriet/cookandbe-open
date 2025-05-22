#ifndef ALGORITHM_DARWIN_MUTATIONS_MUTATION_H_
# define ALGORITHM_DARWIN_MUTATIONS_MUTATION_H_

# include "hippocrate/controls/algorithm/darwin/operator.h"

class DarwinAlgorithm;

class Mutation : public GeneticOperator
{
public:
  explicit          Mutation(DarwinAlgorithm * algorithm) : GeneticOperator(algorithm) {}
  virtual           ~Mutation() {}

  // Mutate individual and returns the number of mutants generated
  virtual int       mutate(const Solution * individual) = 0;

protected:
};

class RandomMutation : public Mutation
{
public:
  explicit          RandomMutation(DarwinAlgorithm * algorithm) : Mutation(algorithm) {}
  virtual           ~RandomMutation() {}

  int               mutate(const Solution * individual);
};

class ScoreOrientedMutation : public Mutation
{
public:
  explicit          ScoreOrientedMutation(DarwinAlgorithm * algorithm) : Mutation(algorithm) {}
  virtual           ~ScoreOrientedMutation() {}

  int               mutate(const Solution * individual);
};

#endif