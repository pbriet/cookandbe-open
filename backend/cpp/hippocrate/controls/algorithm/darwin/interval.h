#ifndef HIPPOCRATE_DARWIN_NUTRIENT_H_
# define HIPPOCRATE_DARWIN_NUTRIENT_H_

# include "hippocrate/models/solution.h"
# include "hippocrate/models/dishindex.h"
# include "hippocrate/models/constraints/nutrient.h"

class IntervalRuleImprover
{
public:
  IntervalRuleImprover(const IntervalRule *r, Solution *s, long _dish_id):
      rule(r), solution(s), dish_id(_dish_id) {};

  bool apply();
  

  const IntervalRule                * rule;
  Solution *                        solution;
  long                              dish_id;
  
  double                            all_dishes_value; // Current "data" value for all the dishes covered by the rule
  double                            current_value;    // Current "data" value for this dish-recipe
  double                            target_value;     // Ideal value that we want for the dish-recipe
  double                            variance;
  
  const RecipeData *                recipe; // Recipe selected for improvement
  
private:
  
  void compute_target_value();
  
  bool apply_switch_dish();
  bool apply_change_ratio();
};


#endif