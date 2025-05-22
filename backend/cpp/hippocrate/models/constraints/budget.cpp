
#include <boost/python.hpp>

#include "hippocrate/models/constraints/budget.h"
#include "hippocrate/models/recipe.h"
#include "hippocrate/models/solution.h"

/*
 * Creates one unique constraint on all dishes
 */
void BudgetConstraint::init_rules(DishIndex * dish_index)
{
  // Here, we apply the rule on mutable ids
  // This means it's not optimal in case there are very few dishes mutable
  // But it's clearly faster
  this->add_rule(new BudgetRule(dish_index, this->max_per_dish * dish_index->mutable_dish_ids.size(),
                                dish_index->mutable_dish_ids, this->cost_per_excess));
}

/*
 * Returns the number of minutes in excess in a given solution
 */
double    BudgetRule::cost_over_max(double value) const
{
  if (this->max_value <= 0 || value <= this->max_value) {
    return 0; // No max or value under max
  }
  double over = value - this->max_value;
  return over * over * this->cost_per_excess;
}

/*
 * Exposes functions/class/methods to Python
 */
void
export_budget_constraint()
{
    using namespace boost::python;
    class_< BudgetConstraint, boost::noncopyable, bases<GenericConstraint> >("BudgetConstraint",
                           init<double, double>((arg("max_per_dish"), arg("cost_per_excess"))));

    // ?? Declaring bases<IntervalRule> raises a weird exception during core import...
    class_< BudgetRule, boost::noncopyable, bases<Rule> >("BudgetRule", no_init);
}