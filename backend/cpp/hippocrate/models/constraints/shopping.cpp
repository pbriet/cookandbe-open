
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <iostream>
#include <map>

#include "hippocrate/tools/container.h"
#include "hippocrate/models/constraints/shopping.h"
#include "hippocrate/models/recipe.h"
#include "hippocrate/models/solution.h"

/*
 * Creates one constraint per dish type
 */
void
ShoppingConstraint::init_rules(DishIndex * dish_index) {
  this->add_rule(new ShoppingRule(dish_index, this, dish_index->all_dish_ids));
}

long
ShoppingConstraint::nb_items(const Solution *s) const {
  long res = 0;
  for (Rule * rule : this->rules)
  {
    ShoppingRule * sub_unicity = dynamic_cast<ShoppingRule *>(rule);
    ASSERT(sub_unicity, "sub constraint of ShoppingConstraint is not ShoppingRule");
    res += sub_unicity->nb_items(s);
  }
  return res;
}

void
ShoppingRule::count_items(FoodIndex::FoodGrams & items, const Solution *s) const {
  // print("count_items", this->dish_ids.size(), this->parent->food_index->minimums.size());
  for (hp::Id dish_id: this->dish_ids) {
    for (const RecipeData * recipe: s->get_recipe_list(dish_id)) {
      for (auto food: recipe->foods) {
        if (this->parent->food_index->has_food(food.first)) {
          items[food.first] += food.second;
        }
      }
    }
  }
}

long
ShoppingRule::eval(const Solution *s) const {
  FoodIndex::FoodGrams  items;
  int size_penalty = 0;
  int amount_penalty = 0;
  
  this->count_items(items, s);
  if (this->parent->items_limit > 0 && this->parent->items_limit < items.size()) {
    // Applying quadratic penalty for items exceeding limit
    size_penalty = std::pow(items.size() - this->parent->items_limit, 1) * this->parent->cost_per_exceeding_item;
  }
  if (this->parent->cost_per_amount_deficit > 0) {
    for (auto food: items) {
      amount_penalty += this->parent->food_index->compute_penalty(food.first, food.second, this->parent->cost_per_amount_deficit);
    }
  }
  // print("ShoppingRule", items.size(), size_penalty, amount_penalty);
  return size_penalty + amount_penalty;
}

long
ShoppingRule::nb_items(const Solution *s) const {
  FoodIndex::FoodGrams  items;
  
  this->count_items(items, s);
  return items.size();
}

/*
 * Exposes functions/class/methods to Python
 */
void export_shopping_constraint()
{
  using namespace boost::python;
    
  class_<ShoppingConstraint, ShoppingConstraint *, boost::noncopyable, bases<GenericConstraint> >(
      "ShoppingConstraint", init<FoodIndex *, int, int, int>(
        (arg("items_limit"), arg("cost_per_exceeding_item"), arg("cost_per_amount_deficit"))
      )
    )
    .def_readonly("cost_per_exceeding_item",  &ShoppingConstraint::cost_per_exceeding_item)
    .def_readonly("cost_per_amount_deficit",  &ShoppingConstraint::cost_per_amount_deficit)
    .def_readonly("items_limit",              &ShoppingConstraint::items_limit)
    .def_readwrite("food_index",              &ShoppingConstraint::food_index)
    .def("nb_items",                          &ShoppingConstraint::nb_items)
  ;

  class_<ShoppingRule, boost::noncopyable, bases<Rule> >("ShoppingRule", no_init)
  ;

}
