#ifndef HP_MEAL_TYPE_BALANCE_H_
# define HP_MEAL_TYPE_BALANCE_H_

# include "hippocrate/models/dataindexer.h"
# include "hippocrate/models/constraints/constraint.h"
# include "hippocrate/tools/container.h"

/*
 * Constraint that ensure a correct balance - on calories - between lunch and dinner
 */
class MealTypeBalanceConstraint : public GenericConstraint
{
public:
  MealTypeBalanceConstraint(const std::string &_nutrient_key, double _min_ratio, double _max_ratio, long _cost_per_perc_out, long _max_penalty):
    GenericConstraint(),
    nutrient_key(_nutrient_key),
    data_id(RecipeDataIndexer::instance[_nutrient_key]),
    min_ratio(_min_ratio),
    max_ratio(_max_ratio),
    cost_per_perc_out(_cost_per_perc_out),
    max_penalty(_max_penalty),
    dish_index(nullptr)
  {}

  virtual void              init_rules(DishIndex * dish_index) override;
  virtual std::string       description() const override { return "Week meal type balance"; }

  const std::string         nutrient_key;
  const long                data_id;
  const double              min_ratio;
  const double              max_ratio;
  const long                cost_per_perc_out;
  const long                max_penalty;
  const DishIndex           * dish_index;
};


class WeekMealTypeBalanceRule : public Rule
{
public:
  WeekMealTypeBalanceRule(const DishIndex *di, const MealTypeBalanceConstraint *_parent, hp::Id _meal_type_id):
    Rule(di, get_all_dishes_from_meal_type(_parent->dish_index, _meal_type_id, _parent->dish_index->external_meal_ids)),
    parent(_parent),
    meal_type_id(_meal_type_id)
  {}

  virtual long                    eval(const Solution *s) const override final;
  virtual std::string             description(bool detailed=true) const override { return "Week meal type balance"; }
  static hp::Ids                  get_all_dishes_from_meal_type(const DishIndex * dish_index, hp::Id meal_type_id, const hp::IdsSet & excluded_meals);

  const MealTypeBalanceConstraint * parent;
  const hp::Id                    meal_type_id;

private:
  double                          calc_nutrient(const Solution *s, const hp::Id) const;
};

void export_meal_type_balance_constraint();

#endif