#ifndef HIPPOCRATE_DARWIN_OTHER_H_
# define HIPPOCRATE_DARWIN_OTHER_H_

# include "hippocrate/models/solution.h"
# include "hippocrate/models/dishindex.h"
# include "hippocrate/models/constraints/redundancy.h"

class RedundancyConstraintImprover
{
public:
  RedundancyConstraintImprover(const RedundancyRule *d, Solution *s, long _dish_id):
      constraint(d), solution(s), dish_id(_dish_id) {};

  bool apply();

  const RedundancyRule *  constraint;
  Solution *                           solution;
  long                                 dish_id;
  
};


#endif