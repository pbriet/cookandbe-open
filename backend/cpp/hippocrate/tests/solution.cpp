#include <boost/test/unit_test.hpp>
#include <boost/test/output_test_stream.hpp>
#include <vector>

#include "hippocrate/models/solution.h"
#include "hippocrate/tools/print.h"

#include "hippocrate/tests/solution.h"

BOOST_AUTO_TEST_SUITE(simple_solution)


/*
 * Simple test of a perfectly random solution, but with one choice only for each dish type.
 * (perfectly deterministic then)
 */
BOOST_AUTO_TEST_CASE(randomize)
{
  DishIndex di;
  long profile_id = 1;
  
  // dish_id, day, meal_id, meal_type_id, dish_type_id
  di.quick_add_dish(1, 1, 1, 1, profile_id, 1);
  di.quick_add_dish(2, 1, 1, 1, profile_id, 2);
  di.quick_add_dish(3, 1, 2, 2, profile_id, 1);
  di.set_fully_mutable();

  RecipeData recipe1(55);
  recipe1.dish_type_ids = { 1, 5 };
  RecipeData recipe2(56);
  recipe2.dish_type_ids = { 2 };
  RecipeList recipes = { &recipe1, &recipe2 };
  
  Problem p(&di);
  p.init_dishdomains(recipes, true);
  p.set_profile_ratio(profile_id, 1.0);
  p.set_main_profile_id(profile_id);
  Solution s(&p);
  s.randomize();
  BOOST_CHECK_EQUAL(s.get_nb_dishes(), (uint) 3);
  
  const Solution::DishToRecipes & dish_recipes = s.get_all_recipes();
  
  BOOST_CHECK_EQUAL(dish_recipes.at(1).size(), (uint) 1);
  BOOST_CHECK_EQUAL(dish_recipes.at(1).at(0), &recipe1);
  
  BOOST_CHECK_EQUAL(dish_recipes.at(2).size(), (uint) 1);
  BOOST_CHECK_EQUAL(dish_recipes.at(2).at(0), &recipe2);
  
  BOOST_CHECK_EQUAL(dish_recipes.at(3).size(), (uint) 1);
  BOOST_CHECK_EQUAL(dish_recipes.at(3).at(0), &recipe1);
}

BOOST_AUTO_TEST_SUITE_END()


BOOST_FIXTURE_TEST_SUITE(aggregated_solutions, AggregatedDishesFixture)
/*
 * Test randomization with one dish, but with a dish type
 * which is aggregated
 *
 * Warning: non-deterministic test
 */
BOOST_AUTO_TEST_CASE(randomize_with_aggregated_dishtype)
{
  Solution s(this->problem);

  uint nb_one_recipe = 0; // Number of times the aggregated dish_type is chosen
  uint nb_two_recipes = 0;  // Number of times the splitted dish types are chosen
  
  for (uint i = 0; i < 100; i++)
  {
    if (i % 2 == 0)
    {
      // Every two iterations, clear the dish_id_to_recipes, to simulate first initialization
      s.clear();
      s.init_dish_ratios();
    }

    s.randomize();
    BOOST_REQUIRE(s.get_nb_dishes() == 1);
    if (s.get_recipe_list(1).size() == 1)
    {
      // Aggregated -> can only be recipe_agg
      BOOST_CHECK_EQUAL(s.get_recipe(1, 0), &(this->recipe_agg));
      nb_one_recipe++;
    }
    else if (s.get_recipe_list(1).size() == 2)
    {
      // Splitted -> can only be recipe1 + recipe2
      BOOST_CHECK_EQUAL(s.get_recipe(1, 0), &(this->recipe1));
      BOOST_CHECK_EQUAL(s.get_recipe(1, 1), &(this->recipe2));
      nb_two_recipes++;
    }
    else
      BOOST_REQUIRE(false);
  }

  // Check that distribution of aggregated / non-aggregated is sensible
  BOOST_REQUIRE(((double)nb_one_recipe) / 100 >= 0.3);
  BOOST_REQUIRE(((double)nb_two_recipes) / 100 >= 0.3);
  
}


BOOST_AUTO_TEST_CASE(solution_validity)
{
  Solution s(this->problem);

  // Empty: wrong
  BOOST_REQUIRE(!s.isValid());
  
  // Only a sub-dish : wrong
  s.set_recipe_list(1, { &(this->recipe1) });
  BOOST_REQUIRE(!s.isValid());
  s.set_recipe_list(1, { &(this->recipe2) });
  BOOST_REQUIRE(!s.isValid());

  // Too many recipes
  s.set_recipe_list(1, { &(this->recipe1), &(this->recipe1), &(this->recipe2) });
  BOOST_REQUIRE(!s.isValid());

  // Correct and splitted
  s.set_recipe_list(1, { &(this->recipe1), &(this->recipe2) });
  BOOST_REQUIRE(s.isValid());

  // Correct and aggregated
  s.set_recipe_list(1, { &(this->recipe_agg) });
  BOOST_REQUIRE(s.isValid());

  // aggregated + splitted: wrong  --  not handled yet
//   s.set_recipe_list(1, { &(this->recipe_agg), &(this->recipe1) });
//   BOOST_REQUIRE(!s.isValid());
//   s.set_recipe_list(1, { &(this->recipe1), &(this->recipe_agg) });
//   BOOST_REQUIRE(!s.isValid());
}

BOOST_AUTO_TEST_SUITE_END() // aggregated_solutions
