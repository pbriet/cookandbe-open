
#include "hippocrate/controls/algorithm/naive/naive.h"
#include "hippocrate/models/problem.h"
#include "hippocrate/models/solution.h"

/*
 * Algorithm: setting random recipe to each dish
 * (corresponding to dish type)
 */
Solution     NaiveAlgorithm::solve()
{
  Solution result(this->problem);
  result.randomize();
  return result;
}