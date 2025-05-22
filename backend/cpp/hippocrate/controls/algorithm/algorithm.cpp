
#include "hippocrate/controls/algorithm/algorithm.h"
#include "hippocrate/models/problem.h"


hp::Clock::time_point
Algorithm::start_solving_time() {
  this->solving_start_time = hp::Clock::now();
  return this->solving_start_time;
}

bool
Algorithm::solving_time_exceeded() const {
  if (this->problem->maximum_solving_time == 0) {
    return false;
  }
  ASSERT(this->solving_start_time > hp::Clock::time_point(), "execution time not initialized, please call start_execution_time() first");
  hp::milliseconds elapsed_time     = std::chrono::duration_cast<hp::milliseconds>(hp::Clock::now() - this->solving_start_time);
  hp::milliseconds maximum_duration = std::chrono::duration_cast<hp::milliseconds>(hp::milliseconds(this->problem->maximum_solving_time));
  return elapsed_time > maximum_duration;
}
