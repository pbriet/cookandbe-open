
#include <boost/python.hpp>

#include "hippocrate/models/constraints/nutrient_balance.h"
#include "hippocrate/models/solution.h"
  
void
NutrientBalanceConstraint::init_rules(DishIndex * dish_index)
{
  this->dish_index = dish_index;
  
  if (!this->meal_constraint) {
    // The balance is computed on a daily basis
    for (auto pair: this->dish_index->dish_ids_per_day) {
      hp::Id  day_id = pair.first;
      DayNutrientBalanceRule * m = new DayNutrientBalanceRule(dish_index, this, day_id);
      this->add_rule(m);
    }
  } else {
    // The balance is computed on a meal basis
    for (auto pair: this->dish_index->dish_ids_per_meal) {
      hp::Id  meal_id = pair.first;
      MealNutrientBalanceRule * m = new MealNutrientBalanceRule(dish_index, this, meal_id);
      this->add_rule(m);
    }
  }
}

long
NutrientBalanceRule::eval(const Solution *s) const
{
  double    nutrient_score = this->calc_nutrient(s, this->parent->data_id);
  double    referent_score = this->calc_nutrient(s, this->parent->referent_id);
  double    nutrient_ratio = nutrient_score / referent_score;
  
  if (!(nutrient_score > 0.0 && referent_score > 0.0)) { return this->parent->max_penalty; }
  if (nutrient_ratio > this->parent->max_ratio) { return 100 * this->parent->cost_per_perc_out * (nutrient_ratio - this->parent->max_ratio); }
  if (nutrient_ratio < this->parent->min_ratio) { return 100 * this->parent->cost_per_perc_out * (this->parent->min_ratio - nutrient_ratio); }
  return 0.0;
}

hp::Ids
DayNutrientBalanceRule::get_all_dishes_from_day(const DishIndex * dish_index, hp::Id day_id) {
  return dish_index->dish_ids_per_day.at(day_id);
}

double
DayNutrientBalanceRule::calc_nutrient(const Solution *s, const hp::Id data_id) const
{
  double res = 0.0;
  
  for (hp::Id dish_id: this->parent->dish_index->dish_ids_per_day.at(this->day_id)) {
    for (const RecipeData * recipe : s->get_recipe_list(dish_id)) {
      res += recipe->get_data(data_id, s->get_main_profile_recipe_ratio(dish_id));
    }
  }
  return res;
};

hp::Ids
MealNutrientBalanceRule::get_all_dishes_from_day(const DishIndex * dish_index, hp::Id meal_id) {
  return dish_index->dish_ids_per_meal.at(meal_id);
}

double
MealNutrientBalanceRule::calc_nutrient(const Solution *s, const hp::Id data_id) const
{
  double res = 0.0;
  
  for (hp::Id dish_id: this->parent->dish_index->dish_ids_per_meal.at(this->meal_id)) {
    for (const RecipeData * recipe : s->get_recipe_list(dish_id)) {
      res += recipe->get_data(data_id, s->get_main_profile_recipe_ratio(dish_id));
    }
  }
  return res;
};

/*
 * Exposes functions/class/methods to Python
 */
void export_nutrient_balance_constraint()
{
  using namespace boost::python;

  class_< NutrientBalanceConstraint, boost::noncopyable, bases<GenericConstraint> >("NutrientBalanceConstraint",
              init<const std::string, const std::string, double, double, long, long, bool>((
                arg("data_key"), arg("referent_key"), arg("min_ratio") = 0.90,
                arg("max_ratio") = 1.10, arg("cost_per_perc_out") = 100, arg("max_penalty") = 10000,
                arg("meal_constraint") = false)));

  class_< NutrientBalanceRule,
          boost::noncopyable, bases<Rule> >("NutrientBalanceRule", no_init)
    .def_readonly("parent", &NutrientBalanceRule::parent);

  class_< DayNutrientBalanceRule,
          boost::noncopyable, bases<NutrientBalanceRule> >("DayNutrientBalanceRule", no_init)
    .def_readonly("day_id", &DayNutrientBalanceRule::day_id);

  class_< MealNutrientBalanceRule,
          boost::noncopyable, bases<NutrientBalanceRule> >("MealNutrientBalanceRule", no_init)
    .def_readonly("meal_id", &MealNutrientBalanceRule::meal_id);
}