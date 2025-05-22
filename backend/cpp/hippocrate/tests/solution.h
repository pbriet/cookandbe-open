
#ifndef TESTS_SOLUTION_H_
# define TESTS_SOLUTION_H_

# include "hippocrate/models/dishindex.h"
# include "hippocrate/models/recipeindex.h"
# include "hippocrate/models/recipe.h"
# include "hippocrate/models/problem.h"

/*
 * Fixture:
 * 3 dish types, the third one being an aggregation of the first two.
 * 3 recipes, one for each dish type
 *
 * 1 dish only, with aggregated dish type
 *
 * A problem available with these data (this->problem)
 */
class AggregatedDishesFixture
{
public:
  AggregatedDishesFixture() {
    long profile_id = 1;
    // Defining a dish with 2 elements (dish type 1 + dish type 2)
    // dish_id, day, meal_id
    Dish *d = new Dish(1, 1, 1, 1, 3, false, false);
    d->add_element_from_dt(1);
    d->add_element_from_dt(2);
    d->add_eater_profile(profile_id);
    d->set_initial_ratio(1.0);
    this->di.add_dish(d);
    this->dish = d;

    // setting an aggregation (dish type 3 == dish type 1 + dish type 2)
    this->di.add_dishtype_aggregation(3, 1);
    this->di.add_dishtype_aggregation(3, 2);
    this->di.set_fully_mutable();

    this->recipe1.dish_type_ids = { 1 };  // Simple dish type
    this->recipe2.dish_type_ids = { 2 };  // Simple dish type
    this->recipe_agg.dish_type_ids = { 3 };  // Aggregated dish type (1 + 2)
    
    RecipeList recipes = { &recipe1, &recipe2, &recipe_agg };

    this->problem = new Problem(&di);
    this->problem->init_dishdomains(recipes, true);
    this->problem->set_profile_ratio(profile_id, 1.0);
    this->problem->set_main_profile_id(profile_id);
  }


  ~AggregatedDishesFixture() {
    delete this->problem;
  }

  DishIndex   di;
  Dish        *dish;
  RecipeData  recipe1 = RecipeData(55);
  RecipeData  recipe2 = RecipeData(56);
  RecipeData  recipe_agg = RecipeData(57);
  RecipeIndex ri;
  Problem *problem;
};

#endif