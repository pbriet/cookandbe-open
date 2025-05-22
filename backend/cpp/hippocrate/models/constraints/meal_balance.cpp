
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

#include "hippocrate/controls/algorithm/darwin/logger.h"
#include "hippocrate/models/constraints/meal_balance.h"
#include "hippocrate/models/problem.h"
#include "hippocrate/models/solution.h"

void MealBalanceConstraint::init_rules(DishIndex *dish_index)
{
  // For each pair (lunch_id, dinner_id), creates a DayMealBalanceRule
  for (auto meal_pair: this->lunch_and_dinners_ids)
  {
    hp::Ids lunch_dish_ids = dish_index->dish_ids_per_meal[meal_pair.first];
    hp::Ids dinner_dish_ids = dish_index->dish_ids_per_meal[meal_pair.second];
    hp::Id  day_id = dish_index->dishes.at(lunch_dish_ids[0])->day_id;
    DayMealBalanceRule *m = new DayMealBalanceRule(dish_index, this, lunch_dish_ids, dinner_dish_ids, day_id);
    this->add_rule(m);
  }
}

long
DayMealBalanceRule::eval(const Solution *s) const
{
  double ratio = this->calc_ratio(s);

  if (ratio > this->parent->max_ratio)
    return round(this->parent->cost_per_perc_out * 100 * (ratio - this->parent->max_ratio));
  if (ratio < this->parent->min_ratio)
    return round(this->parent->cost_per_perc_out * 100 * (this->parent->min_ratio - ratio));
  return 0;
}

/*
* Returns the ratio between lunch and dinner for a given solution
*/
double
DayMealBalanceRule::calc_ratio(const Solution *s) const
{
  double lunch_calories = this->calc_calories(s, this->lunch_dish_ids);
  double dinner_calories = this->calc_calories(s, this->dinner_dish_ids);
  if (lunch_calories < 0.001) {
    if (dinner_calories < 0.001)
      // Return a value which generates no cost
      return (this->parent->min_ratio + this->parent->max_ratio) / 2;
    // Calories not defined on the ingredients of lunch dishes, or no dish at all ?
    return 2;
  }

 return dinner_calories / lunch_calories;
}

double
DayMealBalanceRule::calc_calories(const Solution *s, const hp::Ids dish_ids) const
{
  double res = 0.0;
  for (auto dish_id: dish_ids)
    for (const RecipeData * recipe : s->get_recipe_list(dish_id))
      res += recipe->get_data(this->parent->data_id, s->get_main_profile_recipe_ratio(dish_id));

  return res;
}


bool
DayMealBalanceRule::improve_solution(Solution *s, long dish_id) const
{
  if (s->get_recipe_list(dish_id).size() == 0) {
    return false; // No recipe, how are we supposed to change one ? :/
  }
  double ratio = this->calc_ratio(s);
  double optimal_ratio = (this->parent->min_ratio + this->parent->max_ratio) / 2;
  double lunch_calories = this->calc_calories(s, this->lunch_dish_ids);
  double dinner_calories = this->calc_calories(s, this->dinner_dish_ids);
  double variance = 0;

  float target_value = 0;

  // Modifying one of the dish recipes randomly
  long recipe_no = hp::mod(RandomGenerator::rand(), s->get_recipe_list(dish_id).size());
  const RecipeData * recipe = s->get_recipe(dish_id, recipe_no);

  // Retriveing ratio and current calories for this recipe
  double dish_main_profile_ratio = s->get_main_profile_recipe_ratio(dish_id);
  double current_recipe_calories = recipe->get_data(this->parent->data_id, dish_main_profile_ratio);

  DARWIN_LOG("[improve balance] nb recipes : ", s->get_recipe_list(dish_id).size(),
             " with current recipe calories ", current_recipe_calories);

  // Define the target value by calculating difference between optimal and existing
  if (hp::in_array(this->lunch_dish_ids, dish_id))
  {
      if (ratio == 0)
          return false; // We cannot improve anything, as there is no calories in dinner !
      // We change lunch calories
      target_value = current_recipe_calories + dinner_calories * (1./optimal_ratio - 1./ratio);

      variance = dinner_calories * (1./optimal_ratio - 1./this->parent->max_ratio);

      DARWIN_LOG("[improve balance] Lunch current is : ", lunch_calories, "with_ratio ", ratio);
      DARWIN_LOG("[improve balance] Dinner is : ", dinner_calories);
  }
  else
  {
    ASSERT(hp::in_array(this->dinner_dish_ids, dish_id));
      if (ratio == 0)
          // No calories yet in dinner : go go go
          target_value = lunch_calories * optimal_ratio;
      else
          // We change dinner calories
          target_value = current_recipe_calories + lunch_calories * (optimal_ratio - ratio);

      variance = lunch_calories * (optimal_ratio - this->parent->min_ratio);

      DARWIN_LOG("[improve balance] Dinner current is : ", dinner_calories, "with_ratio ", ratio);
      DARWIN_LOG("[improve balance] Lunch is : ", lunch_calories);
  }

  DARWIN_LOG("[improve balance] Targeting calories : ", target_value, " with variance ", variance, " for optimal ratio ", optimal_ratio);

  // Retrieve the domain + index for this dish/recipe no
  DishIndex *  dish_index = s->problem->dish_index;
  DetailedRecipeIndex *dish_domain_index = dish_index->get_domain(dish_id, s)->indexes[recipe_no];

  // Pick a "random" recipe based on target value
  RecipeData * new_recipe = dish_domain_index->recipe_data_normal(this->parent->data_id, target_value / dish_main_profile_ratio, variance / 2);

  DARWIN_LOG("[improve balance] new_recipe calories : ", new_recipe->get_data(this->parent->data_id, dish_main_profile_ratio));

  // Change recipe
  s->set_recipe(dish_id, recipe_no, new_recipe);

  return true;
}



/*
 * Exposes functions/class/methods to Python
 */
void export_meal_balance_constraint()
{
  using namespace boost::python;

  class_< MealBalanceConstraint, boost::noncopyable, bases<GenericConstraint> >("MealBalanceConstraint",
              init<const std::string, double, double, long>((
                arg("data_key"), arg("min_ratio") = 0.42,
                arg("max_ratio") = 0.48, arg("cost_per_perc_out") = 100)))
       .def("add_lunch_dinner_pair", &MealBalanceConstraint::add_lunch_dinner_pair);

  class_< DayMealBalanceRule,
          boost::noncopyable, bases<Rule> >("DayMealBalanceRule", no_init)
     .def_readonly("day_id", &DayMealBalanceRule::day_id)
     .def_readonly("parent", &DayMealBalanceRule::parent);
}