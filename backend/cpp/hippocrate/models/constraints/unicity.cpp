
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <iostream>
#include <map>

#include "hippocrate/tools/container.h"
#include "hippocrate/controls/algorithm/darwin/other.h"
#include "hippocrate/models/constraints/unicity.h"
#include "hippocrate/models/recipe.h"
#include "hippocrate/models/solution.h"

/*
 * Creates one constraint per dish type
 */
void UnicityConstraint::init_rules(DishIndex * dish_index)
{
  std::set<long>    unique_dish_ids;
  for (auto dish_type_id: this->week_dish_type_ids)
    for (auto dish_id: dish_index->dish_ids_per_dish_type[dish_type_id])
      unique_dish_ids.insert(dish_id);

  // Unique unicity constraint on all the dishes that shouldn't be redundant
  // On entire week
  hp::Ids   vect_dish_ids(unique_dish_ids.begin(), unique_dish_ids.end());
  this->add_rule(new UnicityRule(dish_index, this, vect_dish_ids));

  if (this->day_dish_type_ids.size() == 0) {
    return;
  }

  // Dishes unique day by day
  for (auto day_to_dishes: dish_index->dish_ids_per_day)
  {
    std::set<long>    day_unique_dish_ids;
    for (auto dish_id: day_to_dishes.second)
      if (hp::in_array(this->day_dish_type_ids, dish_id))
        day_unique_dish_ids.insert(dish_id);

    hp::Ids   vect_day_dish_ids(day_unique_dish_ids.begin(), day_unique_dish_ids.end());
    this->add_rule(new UnicityRule(dish_index, this, vect_day_dish_ids));
  }
}

/*
 * Returns the number of redundancies in a given solution
 */
long    UnicityConstraint::nb_redundancies(const Solution *s) const
{
  long res = 0;
  for (auto rule : this->rules)
  {
    UnicityRule * sub_unicity = dynamic_cast<UnicityRule *>(rule);
    ASSERT(sub_unicity, "sub constraint of unicityConstraint is not unicitydishtypeconstraint");
    res += sub_unicity->nb_redundancies(s);
  }
  return res;
}

/*
 * Evaluate a unicity constraint
 */
long
UnicityRule::eval(const Solution *s) const
{
  return this->nb_redundancies(s) * this->parent->cost_per_duplicate;
}

/*
 * Returns the number of redundancies in a given solution
 * redundancy = twice the same recipe
 */
long
UnicityRule::nb_redundancies(const Solution *s) const
{
  // Retrieving all recipes in a set
  std::set<long>        unique_recipes;
  uint                  nb_recipes = 0;
  for (auto dish_id: this->dish_ids)
    for (const RecipeData * recipe: s->get_recipe_list(dish_id))
        if (!(recipe->internal))
        {
            nb_recipes++;
            unique_recipes.insert(recipe->recipe_id);
        }
  // Number of duplicates is the number of dishes minus the number of unique recipes
  return (nb_recipes - unique_recipes.size());
}



/*
 * Creates one constraint per day : avoiding having twice an important food tag appearing
 */
void UnicityFoodTagConstraint::init_rules(DishIndex * dish_index)
{
  for (auto pair : dish_index->dish_ids_per_day)
    this->add_rule(new UnicityFoodTagDailyRule(dish_index, this, pair.second, pair.first));
}

/*
 * Returns the number of redundancies in a given solution
 * redundancy = two recipes sharing the same main food_tag, one of the food_tag given in argument of the parent constraint
 */
long    UnicityFoodTagConstraint::nb_redundancies(const Solution *s) const
{
  long res = 0;
  for (auto rule : this->rules)
  {
    UnicityFoodTagDailyRule * sub_unicity = dynamic_cast<UnicityFoodTagDailyRule *>(rule);
    ASSERT(sub_unicity, "sub constraint of UnicityFoodTagConstraint is not UnicityFoodTagDailyRule");
    res += sub_unicity->nb_redundancies(s);
  }
  return res;
}

/*
 * Evaluate a food tag unicity constraint
 */
long
UnicityFoodTagDailyRule::eval(const Solution *s) const
{
  return this->nb_redundancies(s) * this->parent->cost_per_duplicate;
}

/*
 * Returns the number of redundancies in a given solution
 * redundancy = two recipes sharing the same main food_tag, one of the food_tag given in argument of the parent constraint
 */
long
UnicityFoodTagDailyRule::nb_redundancies(const Solution *s) const
{
  FoodTagOccurences     food_tag_occurences;

  // Calculating the occurences of main food tags over
  // the different recipes of the day
  for (auto dish_id: this->dish_ids)
    for (const RecipeData * recipe: s->get_recipe_list(dish_id))
      for (auto food_tag_id: recipe->main_food_tag_ids)
        food_tag_occurences[food_tag_id]++;

  // For the food_tag_ids that shouldn't be redundant, check if there is more than 1 occurence
  long nb_redundant = 0;
  for (auto food_tag_id: this->parent->food_tag_ids)
    nb_redundant += std::max((long) 0, food_tag_occurences[food_tag_id] - 1);

  return nb_redundant;
}

/*
 * Exposes functions/class/methods to Python
 */
void export_unicity_constraint()
{
    using namespace boost::python;

    class_<hp::Ids>("IdVector")
        .def(vector_indexing_suite<hp::Ids>() );

    class_< UnicityConstraint, UnicityConstraint *, boost::noncopyable, bases<GenericConstraint> >("UnicityConstraint", init<long, hp::Ids, hp::Ids>())
        .def("nb_redundancies", &UnicityConstraint::nb_redundancies);

    class_< UnicityFoodTagConstraint, UnicityFoodTagConstraint *, boost::noncopyable,
            bases<GenericConstraint> >("UnicityFoodTagConstraint", init<long, hp::Ids>())
        .def("nb_redundancies", &UnicityFoodTagConstraint::nb_redundancies);

  class_< UnicityRule,
          boost::noncopyable, bases<Rule> >("UnicityRule", no_init);

  class_< UnicityFoodTagDailyRule,
          boost::noncopyable, bases<Rule> >("UnicityFoodTagDailyRule", no_init)
     .def_readonly("day_id", &UnicityFoodTagDailyRule::day_id);
}
