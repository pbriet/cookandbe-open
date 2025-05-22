#include "dishdomain.h"
#include "hippocrate/models/solution.h"
#include "hippocrate/models/problem.h"
#include "hippocrate/models/filters/filter.h"
#include "hippocrate/tools/print.h"

DishDomain::~DishDomain()
{
  for (auto index: this->indexes)
    delete index;
  delete this->dish_variant;
}

DishDomainOptions::~DishDomainOptions()
{
  for (auto option: this->options)
    delete option;
}

/*
 * Given an existing solution, returns the domain that was used for this solution
 * Example : if the solution contains two recipes Main + side, then it will return the domain with Main + side indexes
 */
DishDomain  * DishDomainOptions::domain_from_solution(const DishIndex * di, const RecipeList &recipes) const
{
  for (auto option: this->options)
  {
    if (option->dish_variant->valid_recipes(di, recipes))
      // The recipes for this dish are compatible with this domain
      return option;
  }
  ASSERT(false, "Couldn't find a domain matching the solution structure");
  return 0;
}

DishDomain  * DishDomainOptions::domain_from_solution(const Solution *s) const
{
  return this->domain_from_solution(s->problem->dish_index, s->get_recipe_list(this->dish_id));
}

bool
DishDomainOptions::check_recipes_in_domain(const DishIndex * di, const RecipeList &recipes) const
{
  long recipe_i = 0;
  for (auto recipe_index: this->domain_from_solution(di, recipes)->indexes)
    if (!(recipe_index->has_recipe(recipes[recipe_i++]->recipe_id)))
      return false;
    
  return true;
}

bool
DishDomainOptions::check_recipes_in_domain(const Solution *s) const
{
  return this->check_recipes_in_domain(s->problem->dish_index, s->get_recipe_list(this->dish_id));
}

/*
Count removable filters and check whether they are sorted correctly
*/
int
DishDomain::nb_removable_filters(const std::list<RecipeFilter *> & recipeFilters) const {
  int  res = 0;
  
  for (const RecipeFilter * filter : recipeFilters) {
    if (!filter->critical) {
      ++res;
    } else {
      if (res != 0) {
        RAISE(hp::InternalError, "Filters are not sorted according to criticity");
      }
    }
  }
  return res;
}

/*
Apply the maximum filters possible
*/
int
DishDomain::apply_recipe_filters(const Dish * dish,
                                 const DishElement * element,
                                 const RecipeList & recipe_list,
                                 const std::list<RecipeFilter *> & allRecipeFilters,
                                 DetailedRecipeIndex * index)
{
  int   max_filters_applied = 0;
  
  for (auto recipe_data: recipe_list) {
    if (element->recipe_compatible(recipe_data)) {
      int nb_filter_applied = 0;
      
      for (const RecipeFilter * filter : allRecipeFilters) {
        if (!filter->accept(dish, recipe_data)) {
          // Can't accept recipes which fails a critical filter
          if (filter->critical) {
            recipe_data = nullptr;
          }
          break;
        }
        // One more filter applied
        ++nb_filter_applied;
      }
      if (nb_filter_applied > max_filters_applied) {
        // We applied more filter than before, new start
        index->clear();
        max_filters_applied = nb_filter_applied;
      }
      // If we pass all criticals and reach the best filter, we add the recipe
      if (recipe_data != nullptr && nb_filter_applied == max_filters_applied) {
        index->add_recipe_data(recipe_data);
      }
    }
  }
  return max_filters_applied;
}

/*
 * Initialize a domain from a dish and a recipe index
 * Returns True if it was possible to enable all the filters
 * IF applying all the filters leads to an empty domain, disabling the last filters  (until there is at least one recipe left)
 */
void
DishDomain::init_from_dish(const RecipeList &recipe_list, const Dish *dish, const std::list<RecipeFilter *> & allRecipeFilters)
{
  int nb_removable_filters    = this->nb_removable_filters(allRecipeFilters);
  int nb_critical_filters     = allRecipeFilters.size() - nb_removable_filters;
  int nb_min_filters_applied  = nb_removable_filters;
  
  if (recipe_list.size() == 0) {
    RAISE(hp::InternalError, "Empty recipe list in init_from_dish() for dish", dish->dish_id);
  }
  for (auto element: dish->elements)
  {
    DetailedRecipeIndex * index = new DetailedRecipeIndex();

    int nb_filters_applied = this->apply_recipe_filters(dish, element, recipe_list, allRecipeFilters, index);
    if (index->empty()) {
      if (nb_critical_filters == 0) {
        RAISE(hp::InternalError, "Empty domain on dish", dish->dish_id, "dish_type", element->dish_type_id, "(no recipes for element dish_type", element->dish_type_id, "?)");
      }
      ASSERT(nb_critical_filters <= nb_filters_applied, "Internal error, should apply maximum filters without emptying domain");
      RAISE(hp::InternalError, "Critical filters are emptying domain on dish", dish->dish_id, "dish_type", element->dish_type_id,
        ": filters", nb_critical_filters + nb_removable_filters,
        "| criticals", nb_critical_filters,
        "| max_applied", nb_filters_applied
      );
    }
    ASSERT(index->all_recipes.size() > 0, "No recipes for dish ", dish->dish_id);
    index->compute_indexes();
    this->indexes.push_back(index);
    if (nb_filters_applied < nb_min_filters_applied) {
      nb_min_filters_applied = nb_filters_applied;
    }
  }
  this->set_fully_filtered(nb_min_filters_applied == nb_removable_filters);
}
