#ifndef HIPPOCRATE_DISHRECIPE_H_
# define HIPPOCRATE_DISHRECIPE_H_

# include "hippocrate/models/recipe.h"

/*
 * Class representing part of the result of the algorithm for a given dish
 * Like equivalent Python-class
 */

class DishRecipe
{ 
public:
  DishRecipe(long dish_id_, RecipeData* recipe_, long order_, double ratio_, bool fully_filtered_) :
     dish_id(dish_id_), recipe(recipe_), order(order_), ratio(ratio_), fully_filtered(fully_filtered_) {}
  
  long          dish_id;
  RecipeData*   recipe;
  long          order;
  double        ratio;
  bool          fully_filtered;
};

void export_dishrecipe();

#endif