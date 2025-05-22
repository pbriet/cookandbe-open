#ifndef SOLUTION_H_
# define SOLUTION_H_

# include <boost/python.hpp>
# include <boost/python/dict.hpp>
# include <string>
# include <iostream>

# include "hippocrate/tools/exception.h"
# include "hippocrate/models/recipe.h"
# include "hippocrate/models/dishrecipe.h"
# include "hippocrate/models/constraints/constraint.h"

class Problem;
class DarwinAlgorithm;

class InvalidSolution : public hp::InternalError {
  public:
    explicit  InvalidSolution(const Infos & infos, const std::string & message) : hp::InternalError(infos, message) {}
};

class Solution
{
public:
  typedef std::vector<RecipeData *>                     RecipeList;
  typedef std::map<long, RecipeList>                    DishToRecipes;
  typedef std::map<long, double>                        RatioDict; // {dish_id : ratio}
  typedef std::map<const Rule *, double>                ConstraintDoubleBuffer;

  explicit              Solution(Problem *p);
  virtual               ~Solution() {}

  // Warning : complete solution reinitialization (remove all dish recipes and adjustement rates)
  void                  clear();

  Problem               * problem;

  // Check whether or not the solution fits the problem
  bool                  isValid(bool check_domains=false) const;

  // Return the number of dishes to serve
  size_t                get_nb_dishes() const { return this->_dish_id_to_recipes.size(); }
  // Get the nth recipe from a specific dish in the solution
  const RecipeData *    get_recipe(long dish_id, long position) const;
  // Get all recipes of a specific dish in the solution
  const RecipeList &    get_recipe_list(long dish_id) const;
  // Get all DishRecipes associations
  const DishToRecipes & get_all_recipes() const { return this->_dish_id_to_recipes; }
  // Iter over all dish and recipes
  DishToRecipes::const_iterator begin() const { return this->_dish_id_to_recipes.begin(); }
  DishToRecipes::const_iterator end()   const { return this->_dish_id_to_recipes.end(); }
  // Set a new recipe to a specific dish in the solution
  void                  set_recipe(long dish_id, long position, RecipeData * recipe, bool call_handlers=true,
                                                                                     bool monotony_rec=true);
  // Set all recipes of a specific dish in the solution
  void                  set_recipe_list(long dish_id, const RecipeList & recipes, double ratio=-1,
                                        bool monotony_rec=true);
  void                  change_dish_ratio(long dish_id, double new_ratio);
  void                  init_dish_ratios();
  inline void           set_dish_ratio(long dish_id, double value) { this->_dish_ratios[dish_id] = value; }

  // Return the computed ratio to apply to the dish recipe
  double                get_total_recipe_ratio(long dish_id) const;
  double                get_main_profile_recipe_ratio(long dish_id) const;
  void                  set_main_profile_recipe_ratio(long dish_id, double value) { this->_dish_main_profile_ratios[dish_id] = value; }

  // Returns a percentage of similarity between 2 solutions  ([0;1])
  double                similarity(Solution *s);

  // Set random recipes for each dish, corresponding to the correct dish_type
  void                  randomize();
  void                  randomize_dish(long dish_id, const std::vector<hp::Id> *prior_recipe_ids = nullptr);
  void                  randomize_dishrecipe(long dish_id, long recipe_i);
  void                  randomize_out_of_domain();

  // Initialize solution by using favorite recipes. Randomize if not available
  void                  init_from_favorites();

  // Calls handlers on the constraints affected by a change in a dish_id
  void                  call_rm_recipes_handlers(long dish_id);
  void                  call_add_recipes_handlers(long dish_id);
  void                  init_constraint_buffers();

  // Buffer of doubles maintained by the constraints
  ConstraintDoubleBuffer constraint_buffer;

protected:
  // The following contains the solution to all your problems!
  DishToRecipes         _dish_id_to_recipes;
  RatioDict             _dish_ratios;
  RatioDict             _dish_main_profile_ratios;

  void                  call_monotony_recursion(long dish_id);
};


std::ostream & operator << (std::ostream & stream, const Solution & s);

void export_solution();

#endif