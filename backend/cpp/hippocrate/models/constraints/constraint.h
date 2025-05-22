#ifndef CONSTRAINT_H_
# define CONSTRAINT_H_

# include <boost/noncopyable.hpp>
# include <vector>
# include <list>
# include <string>

# include "hippocrate/models/dishindex.h"
# include "hippocrate/models/score.h"

class Solution;

  
/*
 * One constraint applied on a set of dishes
 */
class Rule
{
public:
  virtual               ~Rule() {};
  virtual long           eval(const Solution *s) const = 0;
  virtual std::string    description(bool detailed=true) const = 0;
  void                   set_id(long value) { this->id = value; }

  // Visitor for Darwin. Default is false <> not implemented
  virtual bool           improve_solution(Solution *s, long dish_id) const { return false; }


  /*
   * Handlers called by Solution, when modifications occur
   */
  virtual void           on_solution_new_recipes(Solution *s, long dish_id) const {}
  virtual void           on_solution_rm_recipes(Solution *s, long dish_id)  const {}
  virtual void           on_solution_ratio_change(Solution *s, long dish_id, double _old_ratio, double _new_ratio) const {}
  
  long                   id = -1; // Used for internal purpose, including 'determinism'
  hp::Ids                dish_ids;
  hp::Ids                mutable_dish_ids;

  
protected:
  Rule(const DishIndex *di, hp::Ids d);
};

std::ostream & operator << (std::ostream & stream, const Rule & c);

class GenericConstraint : private boost::noncopyable
{
public:
  std::vector<Rule *>           rules;
  long                          id = -1; // Used for internal purpose, including 'determinism'
  
  /*
   * Creates subsets of constraints
   * Example: "Vitamin C" will split dishes into Rules:
   *           - one per day with at least 75% of ANC
   *           - one per week with at least 100% of ANC
   *
   * This method stores constraints in rules
   */
  virtual void                  init_rules(DishIndex *dish_index) = 0;

  // Returns a description of this constraint
  virtual std::string           description() const = 0;

  /*
   * Fully evaluate the solution with this constraint (all subconstraints)
   */
  void                          add_rule(Rule *dsc);
  long                          eval(const Solution *s, Score *sc) const;
  void                          clear();
  void                          set_id(long value) { this->id = value; }

protected:
  virtual ~GenericConstraint();
  GenericConstraint() : boost::noncopyable() {};
};

void export_base_constraints();


#endif