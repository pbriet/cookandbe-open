#ifndef HIPPOCRATE_DARWIN_TYPES_H_
# define HIPPOCRATE_DARWIN_TYPES_H_

# include <vector>
# include <map>
#include "hippocrate/models/solution.h"
#include "hippocrate/models/score.h"

namespace hp {
  namespace darwin {
    
    typedef std::vector<Solution *>                   Population;
    typedef std::map<const Solution *, Score *>       PopulationScores;
    typedef std::map<long, DishScore>                 DishScores;
    typedef std::vector<const Rule *>    RuleList;
    typedef std::map<const GenericConstraint *, RuleList>  ConstraintsDict;
    
  }
} // !hp

#endif