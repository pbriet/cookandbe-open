#ifndef HIPPOCRATE_SCORE_H_
# define HIPPOCRATE_SCORE_H_

# include <map>

class Rule;
class GenericConstraint;
class Problem;


template <typename T>
class IdComparator {
public:
  IdComparator() {};
  bool operator() (T* lhs, T* rhs) const
  {return lhs->id < rhs->id;}
};

class Score
{
public:
  Score(const Problem &p);
  std::vector<long> by_constraint_id;
  std::vector<long> by_rule_id;
  
  long total = 0;
};

/*
 * Total score of a dish : total score of all the broken constraints
 *                         that are defined on that dish
 */
class DishScore
{
public:
  void add_rule(const Problem &p, const Rule *ds, long score);
  long score;
  bool initialized = false;
  std::vector<long>       cost_by_rule_id;
protected:
  void allocate(const Problem &p);
};

void export_score();

#endif
