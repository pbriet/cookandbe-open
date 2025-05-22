
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <iostream>
#include <map>

#include "hippocrate/tools/container.h"
#include "hippocrate/controls/algorithm/darwin/other.h"
#include "hippocrate/models/constraints/unicity.h"
#include "hippocrate/models/recipe.h"
#include "hippocrate/models/solution.h"

void
RedundancyConstraint::init_rules(DishIndex * dish_index)
{
  hp::Ids       dish_ids;
  dish_ids.reserve(dish_index->all_dish_ids.size());
  for (auto dish_type_id : this->dish_type_ids)
  {
    for (auto dish_id: dish_index->dish_ids_per_dish_type[dish_type_id])
      dish_ids.push_back(dish_id);
  }
  this->add_rule(
    new RedundancyRule(dish_index, this, dish_ids, this->optimal_nb_portions));
}

/*
 * Returning the list of dish ids that are not redundant enough
 */
hp::Ids
RedundancyConstraint::get_weak_dishids(Solution *s) const
{
  hp::IdsSet dish_id_set;

  for (auto rule: this->rules)
  {
    RedundancyRule * r = dynamic_cast<RedundancyRule *>(rule);
    ASSERT(r, "sub constraint of redundancy is not a redundancyDishTypeConstraint");
    for (auto dish_id: r->get_weak_dishids(s))
    {
      dish_id_set.insert(dish_id);
    }
  }

  hp::Ids res(dish_id_set.begin(), dish_id_set.end());
  return res;
}

/*
 * Evaluate a redundancy constraint
 */
long
RedundancyRule::eval(const Solution *s) const
{
  RedundancyRule::RecipePortionCount recipe_portion_map = this->recipe_portion_count(s);

  long cost = 0;
  for (auto recipe_portion: recipe_portion_map)
    if (round(recipe_portion.second) < this->optimal_nb_portions)
    {
      cost += (this->optimal_nb_portions - round(recipe_portion.second)) * this->parent->cost_per_missing_portion;
    }

  return cost;
}

RedundancyRule::RecipePortionCount
RedundancyRule::recipe_portion_count(const Solution *s) const
{
  RedundancyRule::RecipePortionCount recipe_portion_count;

  for (auto dish_id: this->dish_ids)
    for (auto recipe: s->get_recipe_list(dish_id))
      if (recipe->nb_ingredients == 1)
      {
        // Encourage redundancy only on mono-ingredient recipes
        recipe_portion_count[recipe] += s->get_total_recipe_ratio(dish_id);
      }
  return recipe_portion_count;
}


/*
 * Returns the list of dish ids that are not redundant enough
 */
hp::Ids
RedundancyRule::get_weak_dishids(Solution *s) const
{
  RedundancyRule::RecipePortionCount recipe_portion_map = this->recipe_portion_count(s);
  hp::Ids res;

  for (auto dish_id: this->dish_ids)
    for (auto recipe: s->get_recipe_list(dish_id))
       if (round(recipe_portion_map[recipe]) < this->optimal_nb_portions)
       {
         res.push_back(dish_id);
         break;
       }

  return res;
}

bool
RedundancyRule::improve_solution(Solution *s, long dish_id) const
{
  return RedundancyConstraintImprover(this, s, dish_id).apply();
}

/*
 * Exposes functions/class/methods to Python
 */
void export_redundancy_constraint()
{
    using namespace boost::python;

    class_< RedundancyConstraint, RedundancyConstraint *, boost::noncopyable, bases<GenericConstraint> >("RedundancyConstraint", init<long, hp::Ids, long>())
        .def("get_weak_dishids", &RedundancyConstraint::get_weak_dishids);
}
