#ifndef CONSTRAINT_SHOPPING_H_
# define CONSTRAINT_SHOPPING_H_

# include "hippocrate/tools/types.h"
# include "hippocrate/models/constraints/constraint.h"
# include "hippocrate/models/foodindex.h"

/*
 * Constraint on shopping list items
 */
class ShoppingConstraint : public GenericConstraint {
public:
  // Constructor
  ShoppingConstraint(FoodIndex * food_index, int items_limit, int cost_per_exceeding_item, int cost_per_amount_deficit):
    GenericConstraint(),
    food_index(food_index),
    cost_per_exceeding_item(cost_per_exceeding_item),
    cost_per_amount_deficit(cost_per_amount_deficit),
    items_limit(items_limit)
  {}

  // Initialize sub constraints
  virtual void              init_rules(DishIndex * dish_index) override;
  virtual std::string       description() const override { return "Shopping"; }
  long                      nb_items(const Solution *s) const;

  FoodIndex                 * food_index;
  unsigned int              cost_per_exceeding_item;
  unsigned int              cost_per_amount_deficit;
  unsigned int              items_limit;
};

class ShoppingRule : public Rule {
public:
  virtual long              eval(const Solution *s) const override;
  long                      nb_items(const Solution *s) const;
  virtual std::string       description(bool detailed=true) const override  { return "Shopping"; }

  ShoppingRule(const DishIndex *di, ShoppingConstraint *_parent, hp::Ids d):
    Rule(di, d),
    parent(_parent)
  {}

protected:
  const ShoppingConstraint  * parent;
  
  void                      count_items(FoodIndex::FoodGrams & items, const Solution *s) const;
};

void export_shopping_constraint();

#endif