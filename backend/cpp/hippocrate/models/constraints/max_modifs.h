#ifndef CONSTRAINT_MAX_MODIFS_H_
# define CONSTRAINT_MAX_MODIFS_H_

# include "hippocrate/tools/types.h"
# include "hippocrate/models/constraints/constraint.h"

/*
 * Constraint that is limiting the number of modifications of an initial solution
 */
class MaxModifsConstraint : public GenericConstraint
{
public:
  // Constructor
  MaxModifsConstraint(Solution *s, long _max_modifs, long _cost_per_modif, long day_id = 0) :
    GenericConstraint(),
    initial_solution(s),
    max_modifs(_max_modifs),
    day_id(day_id),
    cost_per_modif(_cost_per_modif),
    dish_index(nullptr)
  {}

  // Initialize sub constraints
  virtual void              init_rules(DishIndex * dish_index) override;
  long                      nb_modifs(const Solution *s) const;

  // Convert the constraint using the algorithm in argument
  virtual std::string       description() const override { return "Max modifs"; }

public:
  Solution *                initial_solution;
  long                      max_modifs;
  long                      day_id;
  long                      cost_per_modif;
  const DishIndex           * dish_index;
};


/*
 * Unique dishset constraint
 */
class MaxModifsRule : public Rule
{
public:
  virtual long           eval(const Solution *s) const override;
  virtual std::string    description(bool detailed=true) const override  { return "Max modifs"; }

  MaxModifsRule(const DishIndex *di, MaxModifsConstraint *_parent, hp::Ids d):
    Rule(di, d),
    parent(_parent)
  {}

protected:
  const MaxModifsConstraint    *parent;
};


void export_max_modifs_constraint();

#endif