#ifndef HP_NUTRIENT_BALANCE_H_
# define HP_NUTRIENT_BALANCE_H_

# include "hippocrate/models/constraints/constraint.h"
# include "hippocrate/tools/container.h"

/*
 * Constraint that ensure a correct balance between 2 nutrients
 */
class NutrientBalanceConstraint : public GenericConstraint
{
public:
  NutrientBalanceConstraint(const std::string &data_key, const std::string &referent_key, double _min_ratio, double _max_ratio, long _cost_per_perc_out, long _max_penalty, bool _meal_constraint = false):
    GenericConstraint(),
    data_id(RecipeDataIndexer::instance[data_key]),
    referent_id(RecipeDataIndexer::instance[referent_key]),
    min_ratio(_min_ratio),
    max_ratio(_max_ratio),
    cost_per_perc_out(_cost_per_perc_out),
    max_penalty(_max_penalty),
    meal_constraint(_meal_constraint),
    dish_index(nullptr)
  {}

  virtual void              init_rules(DishIndex * dish_index) override;
  virtual std::string       description() const override { return "Nutrient balance constraint"; }

  const long                data_id;
  const long                referent_id;
  const double              min_ratio;
  const double              max_ratio;
  const long                cost_per_perc_out;
  const long                max_penalty;
  const long                meal_constraint = false; // False == Day, True == Meal
  const DishIndex           * dish_index;
};


class NutrientBalanceRule : public Rule {
public:
  NutrientBalanceRule(const DishIndex *di, const NutrientBalanceConstraint *_parent, const hp::Ids & _dish_ids):
    Rule(di, _dish_ids),
    parent(_parent)
  {}

  virtual long                      eval(const Solution *s) const override final;

  const NutrientBalanceConstraint * parent;

protected:
  virtual double                    calc_nutrient(const Solution *s, const hp::Id) const = 0;
};


class DayNutrientBalanceRule : public NutrientBalanceRule
{
public:
  DayNutrientBalanceRule(const DishIndex *di, const NutrientBalanceConstraint *_parent, hp::Id _day_id):
    NutrientBalanceRule(di, _parent, DayNutrientBalanceRule::get_all_dishes_from_day(_parent->dish_index, _day_id)),
    day_id(_day_id)
  {}

  virtual std::string             description(bool detailed=true) const override { return "Day nutrient balance constraint"; }
  static hp::Ids                  get_all_dishes_from_day(const DishIndex * dish_index, hp::Id day_id);

  const hp::Id                    day_id;

private:
  virtual double                  calc_nutrient(const Solution *s, const hp::Id) const override;
};


class MealNutrientBalanceRule : public NutrientBalanceRule
{
public:
  MealNutrientBalanceRule(const DishIndex *di, const NutrientBalanceConstraint *_parent, hp::Id _meal_id):
    NutrientBalanceRule(di, _parent, MealNutrientBalanceRule::get_all_dishes_from_day(_parent->dish_index, _meal_id)),
    meal_id(_meal_id)
  {}

  virtual std::string             description(bool detailed=true) const override { return "Meal nutrient balance constraint"; }
  static hp::Ids                  get_all_dishes_from_day(const DishIndex * dish_index, hp::Id meal_id);

  const hp::Id                    meal_id;

private:
  virtual double                  calc_nutrient(const Solution *s, const hp::Id) const override;
};

void export_nutrient_balance_constraint();

#endif