#ifndef CONSTRAINT_NUTRIENT_H_
# define CONSTRAINT_NUTRIENT_H_

# include "hippocrate/models/constraints/interval.h"

/*
 * Generic constraint for applying min-max on every day
 */
class NutrientConstraint : public GenericConstraint
{
public:

  NutrientConstraint(
    const std::string  &_data_key,
    double    _min_value,
    double    _max_value,
    double    _daily_tolerance_min,
    double    _daily_tolerance_max,
    double    _cost_per_percent_out,
    bool      _create_weekly_constraint = true
  ):
    GenericConstraint(),
    data_key(_data_key),
    min_value(_min_value), max_value(_max_value),
    daily_tolerance_min(_daily_tolerance_min),
    daily_tolerance_max(_daily_tolerance_max),
    cost_per_percent_out(_cost_per_percent_out),
    create_weekly_constraint(_create_weekly_constraint)
  {
    if (this->min_value > 0 and this->max_value > 0 and this->min_value > this->max_value) {
      RAISE(hp::InternalError, sprint("NutrientConstraint (", _data_key, ") has a min (", _min_value, ") > max (", _max_value, ")"));
    }
  }

  const std::string         data_key;
  double                    min_value = -1;  // No penalty as long as value is bigger than X
  double                    max_value = -1;  // No penalty as long as value is lower than X
  double                    daily_tolerance_min;  // percentage of tolerance in daily constraint (not applied weekly)
  double                    daily_tolerance_max;  // percentage of tolerance in daily constraint (not applied weekly)
  double                    cost_per_percent_out; // cost per unit outside of non-critical boundaries (^2 outside)
  bool                      create_weekly_constraint = true; // creates a strict weekly constraint

  virtual void              init_rules(DishIndex *dish_index) override;
  virtual bool              enable_day_constraints() const;
  virtual std::string       description() const override;
};


/*
 * Generic constraint for applying min-max on every meal of given meal_type
 */
class NutrientMealTypeConstraint : public NutrientConstraint
{
public:
  NutrientMealTypeConstraint(
    const std::string  &data_key,
    long                _meal_type_id,
    double              min_value,
    double              max_value,
    double              cost_per_percent_out
  ):
    NutrientConstraint(data_key, min_value, max_value,
                       0, 0, cost_per_percent_out),
    meal_type_id(_meal_type_id) {};

  long                      meal_type_id;

  virtual void              init_rules(DishIndex *dish_index) override;
  virtual std::string       description() const override;

};

class BaseNutrientRule : public IntervalRule
{
public:
  BaseNutrientRule(
    const DishIndex * di,
    const std::string &data_key,
    double            min_value,
    double            max_value,
    hp::Ids           dish_ids,
    double            _cost_per_percent_out
  ):
    IntervalRule(di, data_key, min_value, max_value, dish_ids, true),
    cost_per_percent_out(_cost_per_percent_out)
  {}

  double                    cost_per_percent_out;
  virtual double            cost_over_max(double value)  const override;
  virtual double            cost_under_min(double value) const override;
};


class NutrientWeekRule : public BaseNutrientRule
{
public:
  NutrientWeekRule(
    const DishIndex  *di,
    const std::string &data_key,
    double            min_value,
    double            max_value,
    hp::Ids           dish_ids,
    double            cost_per_percent_out,
    long              _nb_days
  ):
    BaseNutrientRule(di, data_key, min_value, max_value, dish_ids, cost_per_percent_out),
    nb_days(_nb_days)
  {}

  virtual std::string                  description(bool detailed=true) const override;

  long              nb_days;
};

class NutrientDayRule : public BaseNutrientRule
{
public:
  NutrientDayRule(
    const DishIndex  *di,
    const std::string &data_key,
    double            min_value,
    double            max_value,
    hp::Ids           dish_ids,
    double            cost_per_percent_out,
    long              _day_id
  ):
    BaseNutrientRule(di, data_key, min_value, max_value, dish_ids, cost_per_percent_out),
    day_id(_day_id)
  {}

  virtual std::string                  description(bool detailed=true) const override;

  long                  day_id;
};

class NutrientMealRule : public NutrientDayRule
{
  public:
    NutrientMealRule(
      const DishIndex  *di,
      const std::string &data_key,
      double            min_value,
      double            max_value,
      hp::Ids           dish_ids,
      double            cost_per_percent_out,
      long              day_id,
      long              _meal_id):
      NutrientDayRule(di, data_key, min_value, max_value, dish_ids, cost_per_percent_out, day_id),
      meal_id(_meal_id)
    {}

    virtual std::string                  description(bool detailed=true) const override;

    long                  meal_id;
};


void export_nutrient_constraint();

#endif