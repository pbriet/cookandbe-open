#ifndef PROBLEM_H_
# define PROBLEM_H_

# include <vector>

# include "hippocrate/models/constraints/constraint.h"
# include "hippocrate/models/solution.h"
# include "hippocrate/models/score.h"
# include "hippocrate/tools/stats.h"

class Solution;
class RecipeIndex;
class DishIndex;
class RecipeFilter;

class Problem
{
public:
  typedef std::map<const Rule *,
           const GenericConstraint *>          RuleToGeneric;
  typedef std::map<long, std::list< Rule *> >  DishIdToDsConstraint;
  typedef std::map<long, RecipeData * >        RecipeDataById;
  
  explicit                              Problem(DishIndex * d, uint _maximum_solving_time = 0) :
    dish_index(d), initial_solution(0), maximum_solving_time(_maximum_solving_time) {}
  virtual                               ~Problem() {}

  std::vector<GenericConstraint *>      constraints;
  std::map<long, Rule *>                rules_by_id;
  RuleToGeneric                         rule_to_parent;
  DishIndex *                           dish_index;
  Solution *                            initial_solution = nullptr;
  DishIdToDsConstraint                  rules_by_dish_id;
  long                                  main_profile_id;
  // If true, the optimization algorithms won't try to randomize all the mutable dishes at start
  bool                                  stick_to_initial = false;
  uint                                  maximum_solving_time; // CPU time in milliseconds (0 == no limit)
  std::map<hp::Id, double>              profile_ratios;
  hp::stats::CallDict                   darwinCallStats;
  std::map<hp::Id, long>                darwinPopulationVariationScore;
  std::map<const std::string, long>     darwinConstraintTautness;
  std::map<hp::Id, std::vector<long> >  darwinBestRecipesPerDishTypes;
  std::vector<hp::Id>                   favorite_recipe_ids;
  RecipeDataById                        recipe_by_id;
  
  template <typename AlgorithmT>
  Solution                              solve();

  Score *       eval(const Solution *s, bool check_validity = true);
  
  void          add_constraint(GenericConstraint *);
  void          clear_constraints();
  void          add_filter(RecipeFilter *);
  void          assert_validity() const;
  const Rule *  get_rule(long rule_id) const;
  void          set_profile_consumption_coefficient(long profile_id, double consumption_coefficient);

  void          init_dishdomains(const RecipeList & ri, bool fillIndexes);
  void          set_initial_solution(Solution * solution);
  void          stick_to_initial_solution(bool value=true) { this->stick_to_initial = value; }
  
  void          set_main_profile_id(long value) { this->main_profile_id = value; }
  void          set_profile_ratio(long profile_id, double ratio) { this->profile_ratios[profile_id] = ratio; }
  
  void          add_favorite_recipe(long recipe_id);
  
  void          calc_main_profile_ratios(Solution &s, long dish_id) const;
};

void export_problem();

# include "hippocrate/models/problem.hxx"

#endif