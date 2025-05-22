#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <iostream>
#include <cmath>

#include "hippocrate/tools/container.h"
#include "hippocrate/models/constraints/time.h"
#include "hippocrate/models/recipe.h"
#include "hippocrate/models/solution.h"

TimeConstraint::TimeConstraint(double cost_per_minute)
  : GenericConstraint(), cost_per_minute(cost_per_minute)
{
}

/*
 * Creates one constraint per meal
 */
void TimeConstraint::init_rules(DishIndex * dish_index)
{
  for (auto pair : dish_index->dish_ids_per_meal)
  {
    if (!hp::has_key(this->maximum_prep_times, pair.first))
      continue;
    this->add_rule(new MealTimeRule(dish_index, pair.first, pair.second, "prep_minutes", this->maximum_prep_times.at(pair.first),
                                    this->cost_per_minute));
    this->add_rule(new MealTimeRule(dish_index, pair.first, pair.second, "cook_minutes", this->maximum_cook_times.at(pair.first),
                                    this->cost_per_minute));
    this->add_rule(new MealTimeRule(dish_index, pair.first, pair.second, "rest_minutes", this->maximum_rest_times.at(pair.first),
                                    this->cost_per_minute));
  }
}

bool
TimeConstraint::empty() const
{
  return this->maximum_prep_times.size() + this->maximum_cook_times.size() +
         this->maximum_rest_times.size() == 0;
}

void
TimeConstraint::add_meal_time_limit(long meal_id, long max_prep_minutes,
                                    long max_cook_minutes, long max_rest_minutes)
{
  ASSERT(max_prep_minutes > 0, "Preparation time limit should be higher than 0");
  ASSERT(max_cook_minutes > 0, "Cook time limit should be higher than 0");
  ASSERT(max_rest_minutes > 0, "Rest time limit should be higher than 0");
  this->maximum_prep_times[meal_id] = max_prep_minutes;
  this->maximum_cook_times[meal_id] = max_cook_minutes;
  this->maximum_rest_times[meal_id] = max_rest_minutes;
}

MealTimeRule::MealTimeRule(const DishIndex *di, long meal_id, hp::Ids dish_ids, const std::string &time_key,
                           double max_time, double _cost_per_minute)
  : IntervalRule(di, time_key, -1, max_time, dish_ids, false), meal_id(meal_id), cost_per_minute(_cost_per_minute)
{}

/*
 * Cost over max is "excess * cost**2"
 */
double    MealTimeRule::cost_over_max(double value) const
{
  if (this->max_value <= 0 || value <= this->max_value) {
    return 0; // No max or value under max
  }
  double over = value - this->max_value;
  return over * over * this->cost_per_minute;
}



/*
 * Exposes functions/class/methods to Python
 */
void
export_time_constraint()
{
    using namespace boost::python;
      
    class_< TimeConstraint, TimeConstraint *, boost::noncopyable, bases<GenericConstraint> >("TimeConstraint", init<double>(arg("cost_per_minute")))
        .def("empty",                   & TimeConstraint::empty)
        .def("add_meal_time_limit",     & TimeConstraint::add_meal_time_limit);


    class_< MealTimeRule, MealTimeRule *, boost::noncopyable, bases<IntervalRule> >("MealTimeRule", no_init)
        .def_readonly("meal_id",        & MealTimeRule::meal_id);
}