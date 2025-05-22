#ifndef HIPPOCRATE_CONTROLS_ALGORITHM_H_
# define HIPPOCRATE_CONTROLS_ALGORITHM_H_

# include "hippocrate/tools/types.h"

class Problem;
class Solution;

class Algorithm
{
public:
  explicit            Algorithm(Problem *p): problem(p) {}
  virtual             ~Algorithm() {}

  virtual Solution    solve() = 0;
  
  Problem             * problem;
  
protected:
  hp::Clock::time_point   solving_start_time; // Start solving time in milliseconds

  hp::Clock::time_point   start_solving_time();
  bool                    solving_time_exceeded() const;
};

#endif // HIPPOCRATE_CONTROLS_ALGORITHM_H_