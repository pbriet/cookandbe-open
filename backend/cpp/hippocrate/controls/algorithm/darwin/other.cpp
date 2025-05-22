#include <algorithm>

#include "hippocrate/controls/algorithm/darwin/other.h"
#include "hippocrate/tools/random.h"
#include "hippocrate/models/problem.h"
#include "hippocrate/controls/algorithm/darwin/logger.h"

bool    RedundancyConstraintImprover::apply()
{
  const DishIndex *dish_index = this->solution->problem->dish_index;
  
  // Take the recipes of one of the other dishes
  hp::Ids other_dish_ids = this->constraint->dish_ids;
  hp::remove_from(other_dish_ids, this->dish_id);
  long other_dish_id = RandomGenerator::pick(other_dish_ids);

  ASSERT(this->dish_id != other_dish_id, "Redundancy: replacing a dish by itself...");

  // Use the same recipes
  const RecipeList &recipe_list = this->solution->get_recipe_list(other_dish_id);
  
  if (!dish_index->check_dish_recipes_compatibility(this->dish_id, recipe_list))
  {
    DARWIN_LOG("[improve] Redundancy improvement failed");
    // The recipes of the other dish are not compatible with this one.
    return false;
  }
  this->solution->set_recipe_list(this->dish_id, recipe_list);

  DARWIN_LOG("[improve] Improving redundancy");
  
  return true;
}