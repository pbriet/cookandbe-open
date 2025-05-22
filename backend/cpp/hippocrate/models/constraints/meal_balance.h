#ifndef HP_MEAL_BALANCE_H_
# define HP_MEAL_BALANCE_H_

# include "hippocrate/models/constraints/constraint.h"
# include "hippocrate/tools/container.h"

/*
 * Constraint that ensure a correct balance - on calories - between lunch and dinner
 */
class MealBalanceConstraint : public GenericConstraint
{
public:
  typedef std::vector<std::pair<long, long>> MealPairs;

  MealBalanceConstraint(const std::string &_data_key,
                        double _min_ratio, double _max_ratio, long _cost_per_perc_out):
                        GenericConstraint(),
                        data_key(_data_key),
                        data_id(RecipeDataIndexer::instance[_data_key]),
                        min_ratio(_min_ratio), max_ratio(_max_ratio),
                        cost_per_perc_out(_cost_per_perc_out) {};


  virtual void              init_rules(DishIndex *dish_index) override;
  virtual std::string       description() const override { return "day balance (lunch/dinner)"; }

  void                      add_lunch_dinner_pair(hp::Id lunch_id, hp::Id dinner_id) {
                                  this->lunch_and_dinners_ids.push_back(std::pair<long, long>(lunch_id, dinner_id));
  }

  const std::string         data_key;
  const long                data_id;
  MealPairs                 lunch_and_dinners_ids;
  const double              min_ratio; // Minimum ratio [dinner calories / lunch calories]
  const double              max_ratio;
  const long                cost_per_perc_out;
};


class DayMealBalanceRule : public Rule
{
public:
  DayMealBalanceRule(const DishIndex *di, const MealBalanceConstraint *_parent, hp::Ids _lunch_dish_ids,
                           hp::Ids _dinner_dish_ids, long day_id) :
                             Rule(di, hp::concatenate(_lunch_dish_ids, _dinner_dish_ids)),
                             parent(_parent), lunch_dish_ids(_lunch_dish_ids),
                             dinner_dish_ids(_dinner_dish_ids), day_id(day_id) {};

  virtual long                   eval(const Solution *s) const override final;
  virtual std::string            description(bool detailed=true) const override { return "day meal balance"; }
  virtual bool                   improve_solution(Solution *s, long dish_id) const override;

  const MealBalanceConstraint    *parent;
  const hp::Ids                   lunch_dish_ids;
  const hp::Ids                   dinner_dish_ids;
  long                            day_id;
private:
  double        calc_calories(const Solution *s, const hp::Ids) const;
  double        calc_ratio(const Solution *s) const;
};

void export_meal_balance_constraint();

#endif