#ifndef ALGORITHM_NAIVE_H_
# define ALGORITHM_NAIVE_H_

# include "hippocrate/controls/algorithm/algorithm.h"

class NaiveAlgorithm : public Algorithm
{
public:
  NaiveAlgorithm(Problem *p) : Algorithm(p) {} 
  virtual Solution      solve() override final;
};

#endif