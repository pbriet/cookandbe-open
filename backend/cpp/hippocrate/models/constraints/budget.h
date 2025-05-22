#ifndef HIPPOCRATE_MODELS_CONSTRAINTS_BUDGET_H_
# define HIPPOCRATE_MODELS_CONSTRAINTS_BUDGET_H_

# include "hippocrate/tools/types.h"
# include "hippocrate/models/constraints/interval.h"

/*
 * Constraint on budget
 */
class BudgetConstraint : public GenericConstraint
{
public:
  // Constructor
  BudgetConstraint(double _max_per_dish, double _cost_per_excess) :
          GenericConstraint(), max_per_dish(_max_per_dish),
          cost_per_excess(_cost_per_excess) {};

  // Initialize sub constraints
  virtual void              init_rules(DishIndex * dish_index) override;

  virtual std::string       description() const override { return "BudgetConstraint"; }
  
  
  // Max average budget per dish
  double                    max_per_dish;
  // Penalty per abstract budget excess
  double                    cost_per_excess;
};



class BudgetRule : public IntervalRule
{
public:
  BudgetRule(
    const DishIndex * di,
    double            max_value,
    hp::Ids           dish_ids,
    long              _cost_per_excess
  ):
    IntervalRule(di, "price", -1, max_value, dish_ids, false),
    cost_per_excess(_cost_per_excess)
  {}
  
  virtual std::string       description(bool detailed=true) const override { return "BudgetRule"; }
  
  long                      cost_per_excess;
  virtual double            cost_over_max(double value)  const override;
};

void export_budget_constraint();

#endif // HIPPOCRATE_MODELS_CONSTRAINTS_BUDGET_H_