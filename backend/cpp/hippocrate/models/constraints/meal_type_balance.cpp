
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "hippocrate/models/constraints/meal_type_balance.h"
#include "hippocrate/models/solution.h"
  
void MealTypeBalanceConstraint::init_rules(DishIndex * dish_index)
{
  this->dish_index = dish_index;
  
  for (auto pair: this->dish_index->meal_ids_per_meal_type_id) {
    hp::Id  meal_type_id = pair.first;
    WeekMealTypeBalanceRule * m = new WeekMealTypeBalanceRule(dish_index, this, meal_type_id);
    this->add_rule(m);
  }
}

hp::Ids
WeekMealTypeBalanceRule::get_all_dishes_from_meal_type(const DishIndex * dish_index, hp::Id meal_type_id, const hp::IdsSet & excluded_meals) {
  hp::Ids res;
  
  for (hp::Id meal_id: dish_index->meal_ids_per_meal_type_id.at(meal_type_id)) {
    if (hp::has_key(excluded_meals, meal_id)) {
      continue;
    }
    for (hp::Id dish_id: dish_index->dish_ids_per_meal.at(meal_id)) {
      res.push_back(dish_id);
    }
  }
  return res;
}

long
WeekMealTypeBalanceRule::eval(const Solution *s) const
{
  double    global_cost = 0.0;
  float     meal_score_current, meal_score_ratio, meal_score_prev = -1.0;
  
  for (hp::Id meal_id: this->parent->dish_index->meal_ids_per_meal_type_id.at(this->meal_type_id)) {
    if (hp::has_key(this->parent->dish_index->external_meal_ids, meal_id)) {
      continue;
    }
    // Computing nutrient sum on
    meal_score_current = this->calc_nutrient(s, meal_id);
    if (meal_score_prev < 0.0) {
      // First meal
    } else if (meal_score_prev > 0.0 && meal_score_current > 0.0) {
      // Ensuring variation is within tolerance or penalize
      meal_score_ratio = meal_score_current / meal_score_prev;
      if (meal_score_ratio > this->parent->max_ratio) { global_cost += meal_score_ratio - this->parent->max_ratio; }
      if (meal_score_ratio < this->parent->min_ratio) { global_cost += this->parent->min_ratio - meal_score_ratio; }
    } else {
      // Since one of the meals is set to 0, we apply max_penalty
      // Note: the division by (100 * cost_per_perc_out) is here to revert the final conversion on this sub-score
      global_cost += this->parent->max_penalty / (100 * this->parent->cost_per_perc_out);
    }
    meal_score_prev = meal_score_current;
  }
  // Converting result to score
  return static_cast<long>(round(this->parent->cost_per_perc_out * 100 * global_cost));
}

double
WeekMealTypeBalanceRule::calc_nutrient(const Solution *s, const hp::Id meal_id) const
{
  double res = 0.0;
  
  for (hp::Id dish_id: this->parent->dish_index->dish_ids_per_meal.at(meal_id)) {
    for (const RecipeData * recipe : s->get_recipe_list(dish_id)) {
      res += recipe->get_data(this->parent->data_id, s->get_main_profile_recipe_ratio(dish_id));
    }
  }
  return res;
};

/*
 * Exposes functions/class/methods to Python
 */
void export_meal_type_balance_constraint()
{
  using namespace boost::python;

  class_< MealTypeBalanceConstraint, boost::noncopyable, bases<GenericConstraint> >("MealTypeBalanceConstraint",
              init<const std::string, double, double, long, long>((
                arg("nutrient_key"), arg("min_ratio") = 0.90,
                arg("max_ratio") = 1.10, arg("cost_per_perc_out") = 100, arg("max_penalty") = 10000)));

  class_< WeekMealTypeBalanceRule,
          boost::noncopyable, bases<Rule> >("WeekMealTypeBalanceRule", no_init)
     .def_readonly("meal_type_id", &WeekMealTypeBalanceRule::meal_type_id)
     .def_readonly("parent", &WeekMealTypeBalanceRule::parent);
}