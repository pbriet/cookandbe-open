#ifndef HIPPOCRATE_TOOLS_TYPES_H_
# define HIPPOCRATE_TOOLS_TYPES_H_

# include <vector>
# include <set>
# include <unordered_set>
# include <chrono>

namespace hp {
  typedef long                        Id;
  typedef std::vector<Id>             Ids;
  typedef std::unordered_set<Id>      IdsSet;

  // Time  
  typedef std::chrono::steady_clock   Clock;
  typedef std::chrono::milliseconds   milliseconds;
}

#endif