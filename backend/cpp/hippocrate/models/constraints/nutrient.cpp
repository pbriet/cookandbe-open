
#include <boost/python.hpp>
#include <boost/python/list.hpp>
#include <boost/python/args.hpp>
#include <numeric>
#include <iostream>

#include "hippocrate/models/constraints/nutrient.h"
#include "hippocrate/tools/print.h"
#include "hippocrate/tools/debug.h"
#include "hippocrate/tools/random.h"

void
NutrientConstraint::init_rules(DishIndex *dish_index)
{
  if (this->enable_day_constraints()) {
    ASSERT(this->daily_tolerance_min >= 0 && this->daily_tolerance_min <= 1, "Invalid daily_tolerance_min")
    ASSERT(this->daily_tolerance_max >= 0 && this->daily_tolerance_max <= 1, "Invalid daily_tolerance_max")

    double min_value_modifier =  1.0 - this->daily_tolerance_min;
    double max_value_modifier =  1.0 + this->daily_tolerance_max;

    // For each day, creates a NutrientDayRule
    for (auto day_to_dish_ids_pair: dish_index->dish_ids_per_day)
    {
      NutrientDayRule *n = new NutrientDayRule(dish_index,
                                               this->data_key,
                                               this->min_value * min_value_modifier,
                                               this->max_value * max_value_modifier,
                                               day_to_dish_ids_pair.second,
                                               this->cost_per_percent_out,
                                               day_to_dish_ids_pair.first);
      this->add_rule(n);
    }
  }
  // Creates a NutrientWeekRule over the all week
  if (this->create_weekly_constraint)
  {
    long nb_days = dish_index->dish_ids_per_day.size();
    // Weekly constraints have costs that are divided by two (priority to day balance)
    NutrientWeekRule *n = new NutrientWeekRule(dish_index,
                                               this->data_key,
                                               this->min_value * nb_days,
                                               this->max_value * nb_days,
                                               dish_index->all_dish_ids,
                                               this->cost_per_percent_out / 2,
                                               nb_days);
    this->add_rule(n);
  }
}

bool
NutrientConstraint::enable_day_constraints() const {
  return (this->min_value > 0 && this->daily_tolerance_min < 1 && this->daily_tolerance_min >= 0) ||\
         (this->max_value > 0 && this->daily_tolerance_max < 1 && this->daily_tolerance_max >= 0);
}

void
NutrientMealTypeConstraint::init_rules(DishIndex *dish_index)
{
  // For each meal of the given meal type, add a constraint on all the dishes
  // contained in the meal
  for (auto meal_id: dish_index->meal_ids_per_meal_type_id[meal_type_id])
  {
    NutrientMealRule *n = new NutrientMealRule(dish_index,
                                               this->data_key,
                                               this->min_value,
                                               this->max_value,
                                               dish_index->dish_ids_per_meal[meal_id],
                                               this->cost_per_percent_out,
                                               dish_index->meal_day[meal_id],
                                               meal_id);
    this->add_rule(n);
  }
}

std::string
NutrientConstraint::description() const
{
  std::stringstream ss;
  ss << "Nutrient : " << this->data_key << " | ";
  if (this->min_value != -1)
    ss << this->min_value << " <= ";
  ss << "x";
  if (this->max_value != -1)
    ss << " <= " << this->max_value;
  return ss.str();
}

std::string
NutrientMealTypeConstraint::description() const
{
  std::stringstream ss;
  ss << "Mealtype nutrient (meal_type = " << this->meal_type_id << ") : " << this->data_key << " | ";
  if (this->min_value != -1)
    ss << this->min_value << " <= ";
  ss << "x";
  if (this->max_value != -1)
    ss << " <= " << this->max_value;
  return ss.str();
}


std::string
NutrientDayRule::description(bool detailed) const
{
  std::stringstream     description;
  if (detailed)
    description << "NutrientDayRule(" << this->data_key << ") Day " << this->day_id;
  else
    description << "Day " << this->day_id;
  return description.str();
}

std::string
NutrientMealRule::description(bool detailed) const
{
  std::stringstream     description;
  if (detailed)
    description << "NutrientMealRule(" << this->data_key << ") Day " << this->day_id << " - Meal " << this->meal_id;
  else
    description << "Day " << this->day_id << " - Meal " << this->meal_id;
  return description.str();
}

std::string
NutrientWeekRule::description(bool detailed) const
{
  std::stringstream     description;
  if (detailed)
    description << "NutrientWeekRule(" << this->data_key << ") Week-AVG ";
  else
    description << "Week AVG";
  return description.str();
}

double
BaseNutrientRule::cost_over_max(double value) const
{
  double percentage_diff = IntervalRule::cost_over_max(value);
  return percentage_diff * percentage_diff * this->cost_per_percent_out;
}

double
BaseNutrientRule::cost_under_min(double value) const
{
  double percentage_diff = IntervalRule::cost_under_min(value);
  return percentage_diff * percentage_diff * this->cost_per_percent_out;
}

/*
 * Exposes functions/class/methods to Python
 */
void export_nutrient_constraint()
{
  using namespace boost::python;

  class_< NutrientConstraint, boost::noncopyable, bases<GenericConstraint> >("NutrientConstraint",
            init<const std::string, double, double, double, double, double, bool>((
              arg("data_key"), arg("min_value"), arg("max_value"),
              arg("daily_tolerance_min") = 0.25, arg("daily_tolerance_max") = 0.25,
              arg("cost_per_percent_out") = 10,
              arg("create_weekly_constraint") = true
            )))
     .def("enable_day_constraints", &NutrientConstraint::enable_day_constraints)
     .def_readonly("min_value", &NutrientConstraint::min_value)
     .def_readonly("max_value", &NutrientConstraint::max_value)
     .def_readonly("daily_tolerance_min", &NutrientConstraint::daily_tolerance_min)
     .def_readonly("daily_tolerance_max", &NutrientConstraint::daily_tolerance_max)
     .def_readonly("cost_per_percent_out", &NutrientConstraint::cost_per_percent_out)
     .def_readonly("create_weekly_constraint", &NutrientConstraint::create_weekly_constraint)
     .def_readonly("data_key", &NutrientConstraint::data_key);

  class_< NutrientMealTypeConstraint,
          boost::noncopyable, bases<GenericConstraint> >("NutrientMealTypeConstraint",
               init<const std::string, long, double, double, double>((
                arg("data_key"), arg("meal_type_id"),
                arg("min_value"), arg("max_value"), arg("cost_per_percent_out")
              )))
     .def_readonly("meal_type_id", &NutrientMealTypeConstraint::meal_type_id);

  class_< NutrientWeekRule,
          boost::noncopyable, bases<IntervalRule> >("NutrientWeekRule", no_init)
     .def_readonly("nb_days", &NutrientWeekRule::nb_days);

  class_< NutrientDayRule,
          boost::noncopyable, bases<IntervalRule> >("NutrientDayRule", no_init)
     .def_readonly("day_id", &NutrientDayRule::day_id);

  class_< NutrientMealRule,
          boost::noncopyable, bases<NutrientDayRule> >("NutrientMealRule", no_init)
     .def_readonly("meal_id", &NutrientMealRule::meal_id);
}