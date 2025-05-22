#ifndef HIPPOCRATE_DISH_DOMAIN
# define HIPPOCRATE_DISH_DOMAIN

#include "hippocrate/models/recipeindex.h"
#include "hippocrate/models/dish.h"
#include "hippocrate/tools/random.h"

class Solution;
class RecipeFilter;

/*
 * This class contains a list of indexes to pick into.
 * If this is a simple dish, there'll be one entry.
 * If it's an aggregated dish, there might be more than one.
 */
class DishDomain
{
public:
  explicit  DishDomain(Dish *_dish_variant): dish_variant(_dish_variant) {}
  virtual   ~DishDomain();
  
  void      init_from_dish(const RecipeList &recipe_list, const Dish *dish, const std::list<RecipeFilter *> & recipeFilters);

  bool      isEmpty() { return this->indexes.size() == 0; }
  
  void      set_fully_filtered(bool value) { this->fully_filtered = value; }
  
  std::vector<DetailedRecipeIndex *> indexes;
  
  // dish_variant is the structure of the dish corresponding to this option
  // this is not necessarily one of the original dish, but can be a variant - with some
  // aggregations included
  // In any case, dish_variant->elements.size() == this->indexes.size()
  Dish      * dish_variant;
  
  // Was it able to apply all the filters to build this index ?
  bool      fully_filtered = true;

protected:
  int       nb_removable_filters(const std::list<RecipeFilter *> & recipeFilters) const;
  int       apply_recipe_filters(const Dish * dish, const DishElement * element, const RecipeList & recipe_list, const std::list<RecipeFilter *> & allRecipeFilters, DetailedRecipeIndex * index);
};

/*
 * This class contains the list of different possible domains for the dish
 */
class DishDomainOptions
{
public:
  DishDomainOptions(long _dish_id) : dish_id(_dish_id) {}
  ~DishDomainOptions();

  std::vector<DishDomain *> options;
  long dish_id;
  
  // Randomly returns one of the possible domains
  inline DishDomain       * random_domain() const {
    ASSERT(this->options.size() > 0, "No domain options");
    return RandomGenerator::pick(this->options);
  }

  // Given an existing solution, returns the domain that was used for this solution
  DishDomain              * domain_from_solution(const Solution *s) const;
  DishDomain              * domain_from_solution(const DishIndex * di, const RecipeList &recipes) const;
  bool                      check_recipes_in_domain(const Solution *s) const;
  bool                      check_recipes_in_domain(const DishIndex * di, const RecipeList &recipes) const;
};

#endif