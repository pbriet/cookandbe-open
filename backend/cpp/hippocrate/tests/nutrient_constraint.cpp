#include <boost/test/unit_test.hpp>
#include <boost/test/output_test_stream.hpp>

#include "hippocrate/models/dataindexer.h"
#include "hippocrate/models/recipe.h"
#include "hippocrate/models/recipeindex.h"
#include "hippocrate/models/problem.h"
#include "hippocrate/models/solution.h"
#include "hippocrate/models/constraints/nutrient.h"

BOOST_AUTO_TEST_SUITE(nutrient_constraint_suite)

BOOST_AUTO_TEST_CASE(eval_nutrient)
{
  long profile_id = 1;
  RecipeDataIndexer::instance.reset();
  RecipeDataIndexer::instance.add_to_index("other_nutrient");
  RecipeDataIndexer::instance.add_to_index("my_nutrient");
  RecipeDataIndexer::instance.add_to_index("third_nutrient");

  // Constraint : my_nutrient should be between 5 and 10
  NutrientConstraint n("my_nutrient", 5, 10, 0, 0, 100, false);
  DishIndex dish_index;
  RecipeIndex recipe_index;

  // Adding one unique dish in the planning (dish_id, day, meal_id, meal_type_id, profile_id, dish_type_id)
  dish_index.quick_add_dish(1, 1, 1, 1, profile_id, 1);
  dish_index.set_fully_mutable();

  // Creating one unique recipe with nutrients
  RecipeData the_only_recipe(1);
  the_only_recipe.allocate_data();
  the_only_recipe.add_data("my_nutrient", 13);
  the_only_recipe.add_data("other_nutrient", 7);
  the_only_recipe.add_data("third_nutrient", 2);
  the_only_recipe.dish_type_ids = { 1 };
  RecipeList all_recipe_data = { &the_only_recipe };

  Problem problem(&dish_index);
  problem.set_main_profile_id(profile_id);
  problem.set_profile_ratio(profile_id, 1.0);
  problem.add_constraint(&n);
  problem.init_dishdomains(all_recipe_data, true);
  // Creating a solution with the unique recipe set
  // to the unique dish
  Solution solution(&problem);
  solution.set_recipe_list(1, { &the_only_recipe });

  // Initializing a problem with the nutrient constraint
  // Checking that constraint is returning a cost
  // The nutrient value is 13
  // the value should be between 5 and 10. The value is 3 above, that represents 3/(10-5) = 60% of max value,
  // i.e. penalty=60*100 (cost per percentage out)

  Score * score = problem.eval(&solution);
  BOOST_CHECK_EQUAL(score->total, 100 * 60 * 60);
  delete score;
}

BOOST_AUTO_TEST_SUITE_END()