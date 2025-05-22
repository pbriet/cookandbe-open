#ifndef CONSTRAINT_INTERVAL_H_
# define CONSTRAINT_INTERVAL_H_

# include "hippocrate/models/constraints/constraint.h"
# include "hippocrate/models/solution.h"

/*
 * Generic rule with min max on a data  (RecipeData::get_data)
 * [data indexed by RecipeDataIndexer singleton]
 * 
 * With full optimization for Darwin
 */
class IntervalRule : public Rule
{
public:
  IntervalRule(const DishIndex *di,
               const std::string &_data_key,
               double            _min_value,
               double            _max_value,
               hp::Ids dish_ids,
               bool              _apply_ratio = true
              ) : Rule(di, dish_ids), data_key(_data_key),
                  min_value(_min_value), max_value(_max_value),
                  apply_ratio(_apply_ratio)
    {                            
      if (this->min_value > 0 and this->max_value > 0 and this->min_value > this->max_value) {
        RAISE(hp::InternalError, sprint("IntervalRule (", this->data_key, ") has a min (", _min_value, ") > max (", _max_value, ")"));
      }
    this->data_id = RecipeDataIndexer::instance[_data_key];
    }

  virtual long           eval(const Solution *s) const override final;
  double                 get_value(const Solution *s) const;
  virtual bool           improve_solution(Solution *s, long dish_id) const override;
  double                 calc_value(const Solution *s, long dish_id) const;

  inline double          get_ratio(const Solution *s, long dish_id) const {
    if (!this->apply_ratio)
      return 1.0;
    return s->get_main_profile_recipe_ratio(dish_id);
  }

  virtual void           on_solution_new_recipes(Solution *s, long dish_id) const override;
  virtual void           on_solution_rm_recipes(Solution *s, long dish_id)  const override;
  
  /*
   * Costs calculations : what happens when over/under min/max
   * Default is percentage
   */
  virtual double            cost_over_max(double  value) const;
  virtual double            cost_under_min(double value) const;
  
  const std::string         data_key;
  long                      data_id;
  
  double                    min_value = -1;  // No penalty as long as value is bigger than X
  double                    max_value = -1;  // No penalty as long as value is lower than X
  
  bool                      apply_ratio;
};

void export_interval_rule();

#endif