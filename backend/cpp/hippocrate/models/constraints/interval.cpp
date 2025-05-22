
#include <boost/python.hpp>
#include <boost/python/list.hpp>
#include <boost/python/args.hpp>
#include <numeric>
#include <iostream>

#include "hippocrate/models/constraints/interval.h"
#include "hippocrate/controls/algorithm/darwin/interval.h"
#include "hippocrate/models/solution.h"
#include "hippocrate/models/recipe.h"
#include "hippocrate/models/problem.h"
#include "hippocrate/tools/print.h"
#include "hippocrate/tools/debug.h"
#include "hippocrate/tools/random.h"


/*
 * Default cost methods : percentage over/under
 */
double            IntervalRule::cost_over_max(double value) const
{
  if (this->max_value <= 0 || value <= this->max_value) {
    return 0; // No max or value under max
  }
  if (this->min_value <= 0) {
    return 100 * (value - this->max_value) / this->max_value; // Simple max constraint
  }
  // Max and min
  return 100 * (value - this->max_value) / (this->max_value - this->min_value);
}

double            IntervalRule::cost_under_min(double value) const
{
  if (this->min_value <= 0 || value >= this->min_value)
    return 0; // No min or value over min
  return 100 * (this->min_value - value) / this->min_value;
}


/*
 * For a given solution, returns the value on the constraint data(s)
 */
double   IntervalRule::get_value(const Solution *s) const
{
  // The constraint buffer should contain the sum of nutrient values for all the dishes
  // Dividing it by the number of days
  return s->constraint_buffer.at(this);
}

/*
 * Returns the data value for one dish (sum of the dish recipes)
 */
double
IntervalRule::calc_value(const Solution *s, long dish_id) const
{
  double res = 0.0;
  double ratio = this->get_ratio(s, dish_id);
  for (const RecipeData * recipe : s->get_recipe_list(dish_id)) {
    res += recipe->get_data(this->data_id, ratio);
  }
  return res;
}

bool
IntervalRule::improve_solution(Solution *s, long dish_id) const
{
  return IntervalRuleImprover(this, s, dish_id).apply();
}


void
IntervalRule::on_solution_new_recipes(Solution *s, long dish_id) const
{
  // When there is new recipes in a solution, add its nutrient values in the buffer
  s->constraint_buffer[this] += this->calc_value(s, dish_id);
}

void
IntervalRule::on_solution_rm_recipes(Solution *s, long dish_id)  const
{
  ASSERT(s->constraint_buffer.size() > 0, "Solution buffers seem not to have been initialized. Please check\
                                           that the solution is built once constraints are added in the problem.");
  // When some recipes are removed from a solution, remove its nutrient values from the buffer
  s->constraint_buffer[this] -= this->calc_value(s, dish_id);
}

/*
 * Evaluate a nutrient constraint on a given day
 */
long
IntervalRule::eval(const Solution *s) const
{
  double value = this->get_value(s);
  // Is the data value below the requirement ???
  long low_penalty = this->cost_under_min(value);
  if (low_penalty > 0)
    return low_penalty;
  return this->cost_over_max(value);
}

/*
 * Exposes functions/class/methods to Python
 */
void export_interval_rule()
{
  using namespace boost::python;

  class_< IntervalRule,
          boost::noncopyable, bases<Rule> >("IntervalRule", no_init)
     .def("get_value", &IntervalRule::get_value)
     .def_readonly("min_value",  &IntervalRule::min_value)
     .def_readonly("max_value",  &IntervalRule::max_value)
     .def_readonly("data_key",   &IntervalRule::data_key)
     .def_readonly("data_id",    &IntervalRule::data_id);;
          
}