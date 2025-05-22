#ifndef HIPPOCRATE_MODELS_CONSTRAINTS_TIME_H_
# define HIPPOCRATE_MODELS_CONSTRAINTS_TIME_H_

# include "hippocrate/tools/types.h"
# include "hippocrate/models/constraints/interval.h"

/*
 * Constraint on time of recipes
 */
class TimeConstraint : public GenericConstraint
{
public:
  // Constructor
  TimeConstraint(double cost_per_minute);

  // Initialize sub constraints
  virtual void              init_rules(DishIndex * dish_index) override;

  // Dictionnaire meal_id -> temps maximum 
  std::map<long, long>      maximum_prep_times;
  std::map<long, long>      maximum_cook_times;
  std::map<long, long>      maximum_rest_times;
  
  void                      add_meal_time_limit(long meal_id, long max_prep_minutes,
                                                long max_cook_minutes, long max_rest_minutes);

  virtual std::string       description() const override { return "TimeConstraint"; }
  
  bool                      empty() const;
public:
  // Penalty per recipe exceeding time limit
  double                    cost_per_minute;
};

/*
 * Time dishset constraint on 1 meal, whatever the number of dishes
 */
class MealTimeRule : public IntervalRule
{
public:
  virtual std::string       description(bool detailed = true) const override  { return "MealTime " + this->data_key; }

  MealTimeRule(const DishIndex *di, long meal_id, hp::Ids dish_ids, const std::string &time_key, double max_time,
               double cost_per_minute);
  long                      meal_id;
  double                    cost_per_minute; // Squared
  
  virtual double            cost_over_max(double value)  const override;
};


void export_time_constraint();

#endif // HIPPOCRATE_MODELS_CONSTRAINTS_TIME_H_