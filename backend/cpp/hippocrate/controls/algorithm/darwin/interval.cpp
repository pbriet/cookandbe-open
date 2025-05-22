
#include "hippocrate/controls/algorithm/darwin/config.h"
#include "hippocrate/controls/algorithm/darwin/interval.h"
#include "hippocrate/controls/algorithm/darwin/logger.h"
#include "hippocrate/models/problem.h"
#include "hippocrate/tools/random.h"
#include "hippocrate/tools/container.h"
#include "hippocrate/models/recipeindex.h"

bool    IntervalRuleImprover::apply()
{
#ifdef DEBUG
  DishIndex *  dish_index = this->solution->problem->dish_index;
#endif
  ASSERT(this->solution->isValid(), "Invalid solution");
  if (this->solution->get_recipe_list(this->dish_id).size() == 0)
  {
    // Empty dish (optional elements - no recipes)
    ASSERT(dish_index->domains[this->dish_id]->domain_from_solution(this->solution)->isEmpty(), "No recipe on non-empty domain");
    return false;
  }

  // This is the value we currently have in the solution for this rule  (sum of all dishes)
  this->all_dishes_value = this->rule->get_value(this->solution);

  if (this->rule->apply_ratio && RandomGenerator::in_percentage(DarwinConfig::get<double>("ratio_change_rate")))
    return this->apply_change_ratio(); // improve by changing ratio
  return this->apply_switch_dish();    // improve by changing recipe

}

/*
 * Compute what should be the target value for the selected dish-recipe
 */
void    IntervalRuleImprover::compute_target_value()
{
  double min_requirement = this->rule->min_value;
  double max_requirement = this->rule->max_value;
  double total_target_value;

  ASSERT(min_requirement <= 0 or max_requirement <= 0 or min_requirement < max_requirement,
         "Invalid interval rule (", this->rule->data_id, ") with min_value (", min_requirement, ") > max_value (", max_requirement, ")");

  if (min_requirement > 0 && max_requirement <= 0)
  {
    // Min only. Let's target 125% of min
    total_target_value = min_requirement * 1.25;
    this->variance = min_requirement * 0.25;
    DARWIN_LOG("[improve] Min: ", min_requirement);
  }
  else if (min_requirement > 0 && max_requirement > 0)
  {
    // Min-max
    if (this->all_dishes_value < min_requirement)
      // under min, the objective is 125% of min, or middle of the interval if it's lower
      total_target_value= std::min(min_requirement * 1.25, (min_requirement + max_requirement) / 2);
    else
    {
      ASSERT(this->all_dishes_value >= max_requirement, "Broken rule within min-max ??");
      // Min max and over max, the objective is 75% of max, or middle of the interval if it's higher
      total_target_value = std::max(max_requirement * 0.75, (min_requirement + max_requirement) / 2);
    }
    ASSERT(total_target_value >= min_requirement && total_target_value <= max_requirement, "Optimal value not within the interval !");
    this->variance = std::min(total_target_value - min_requirement, max_requirement - total_target_value);
  }
  else
  {
    // Max only. Let's target 75% of max
    ASSERT(max_requirement > 0, "max_requirement null in interval rule");
    total_target_value = max_requirement * 0.75;
    this->variance = max_requirement * 0.25;
    DARWIN_LOG("[improve] Max: ", max_requirement);
  }

  DARWIN_LOG("[improve] Ideal value (all dishes): ", total_target_value);

  // This is the value we want to get for the dish
  this->target_value = total_target_value - (this->all_dishes_value - current_value);
}


bool    IntervalRuleImprover::apply_switch_dish()
{
  long recipe_no = hp::mod(RandomGenerator::rand(), this->solution->get_recipe_list(this->dish_id).size());

  long data_id = this->rule->data_id;
  this->recipe = this->solution->get_recipe(this->dish_id, recipe_no);

  double dish_main_profile_ratio = this->rule->get_ratio(this->solution, dish_id);
  current_value = this->recipe->get_data(data_id, dish_main_profile_ratio);

  // Compute what is the ideal value we want to target
  this->compute_target_value();

  DishIndex *  dish_index = this->solution->problem->dish_index;

  // The current solution for this dish is based on one of the possible domains (aggregated or not)
  // We retrieve the domain associated to this solution/dish
  DetailedRecipeIndex *dish_domain_index = dish_index->get_domain(this->dish_id, this->solution)->indexes[recipe_no];

  DARWIN_LOG("[improve] Total value is ", this->all_dishes_value);
  DARWIN_LOG("[improve] Selected dish value is ", current_value);
  DARWIN_LOG("[improve] Ideal value (selected dish): ", this->target_value, " (with ratio ", dish_main_profile_ratio, " and this->variance: ", this->variance / 2, ")");

  RecipeData * new_recipe = dish_domain_index->recipe_data_normal(data_id, this->target_value / dish_main_profile_ratio, this->variance / 2);

  if (new_recipe == 0)
  {
    DARWIN_LOG("[improve] no recipe with this data");
    return false;  // Fail !
  }
  DARWIN_LOG("[improve] New recipe value: ", new_recipe->data[data_id], " ( with this->variance: ", this->variance, ")");

  this->solution->set_recipe(this->dish_id, recipe_no, new_recipe);
  return true;
}


bool    IntervalRuleImprover::apply_change_ratio()
{
  double dish_ratio       = this->solution->get_total_recipe_ratio(this->dish_id);
  double min_requirement  = this->rule->min_value;
  double max_requirement  = this->rule->max_value;
  const Dish *  dish      = this->solution->problem->dish_index->dishes.at(this->dish_id);
  ASSERT(dish->initial_global_ratio > 0, "non-initialized global ratio on dish", this->dish_id);
  ASSERT(dish_ratio > 0, "null total recipe ratio on dish", this->dish_id);
  double variation = 1;

  // if (dish->profile_ids.size() == 1)
  //   variation = 0.25;  // 1 eater <> smaller variations

  if (min_requirement > 0 && this->all_dishes_value < min_requirement)
    dish_ratio += variation;
  else if (max_requirement > 0 && this->all_dishes_value > max_requirement)
    dish_ratio -= variation;

  if (dish_ratio < 0.7 || dish_ratio < dish->initial_global_ratio / 2 || dish_ratio > dish->initial_global_ratio * 1.5)
    // Ratio is too far from the initial value
    return false;

  ASSERT(dish_ratio > 0, "null total recipe ratio on dish", this->dish_id);
  this->solution->change_dish_ratio(this->dish_id, dish_ratio);

  return true;
}