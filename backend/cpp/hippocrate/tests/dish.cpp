#include <boost/test/unit_test.hpp>
#include "hippocrate/tests/solution.h"

BOOST_FIXTURE_TEST_SUITE(dishes, AggregatedDishesFixture)
/*
 * Test the dish object
 */
BOOST_AUTO_TEST_CASE(compatibility_with_recipes)
{
  // The first element of the dish has a dish_type 1, like the recipe1
  BOOST_CHECK_EQUAL(this->dish->elements.front()->recipe_compatible(&(this->recipe1)), true);
  BOOST_CHECK_EQUAL(this->dish->elements.front()->recipe_compatible(&(this->recipe2)), false);
  BOOST_CHECK_EQUAL(this->dish->elements.front()->recipe_compatible(&(this->recipe_agg)), false);
  
  BOOST_CHECK_EQUAL(this->dish->elements.back()->recipe_compatible(&(this->recipe1)), false);
  BOOST_CHECK_EQUAL(this->dish->elements.back()->recipe_compatible(&(this->recipe2)), true);
  BOOST_CHECK_EQUAL(this->dish->elements.back()->recipe_compatible(&(this->recipe_agg)), false);

  RecipeList good_recipes_splitted = { &(this->recipe1), &(this->recipe2) };
  RecipeList bad_recipes_splitted = { &(this->recipe2), &(this->recipe1) };
  RecipeList bad_recipes_solo = { &(this->recipe2) };
  RecipeList good_recipes_aggregated = { &(this->recipe_agg) };

  // Fit perfectly the structure of the dish  [recipe1 + recipe2]
  BOOST_CHECK_EQUAL(this->dish->valid_recipes(&(this->di), good_recipes_splitted), true);
  BOOST_CHECK_EQUAL(this->dish->valid_recipes_any_variant(&(this->di), good_recipes_splitted), true);
  // Doesn't fit the structure
  // recipe2 + recipe1
  BOOST_CHECK_EQUAL(this->dish->valid_recipes(&(this->di), bad_recipes_splitted), false);
  BOOST_CHECK_EQUAL(this->dish->valid_recipes_any_variant(&(this->di), bad_recipes_splitted), false);
  // Doesn't fit the structure
  // recipe2
  BOOST_CHECK_EQUAL(this->dish->valid_recipes(&(this->di), bad_recipes_solo), false);
  BOOST_CHECK_EQUAL(this->dish->valid_recipes_any_variant(&(this->di), bad_recipes_solo), false);
  // Doesn't fit the structure, but fit one of the aggregated variant
  // recipe_agg
  BOOST_CHECK_EQUAL(this->dish->valid_recipes(&(this->di), good_recipes_aggregated), false);
  BOOST_CHECK_EQUAL(this->dish->valid_recipes_any_variant(&(this->di), good_recipes_aggregated), true);
}


BOOST_AUTO_TEST_CASE(variants)
{
  std::list<Dish *> variants = this->dish->get_dish_variants(&(this->di));
  BOOST_REQUIRE(variants.size() == 2);
  // First variant is the original one
  BOOST_REQUIRE(variants.front()->elements.size() == 2);
  // Second variant is the aggregated one
  BOOST_REQUIRE(variants.back()->elements.size() == 1);
  // Cleaning
  for (Dish * dish : variants)
    delete dish;
}


BOOST_AUTO_TEST_CASE(optional_elements)
{
  Dish *d = new Dish(1, 1, 1, 1, 1, true, false); // Dish which is optional
  DishElement *e1 = new DishElement(7); // Dish type 7
  d->add_element(e1);

  DishIndex   di;
  di.add_dish(d);
  di.set_fully_mutable();

  std::list<Dish *> variants = d->get_dish_variants(&(this->di));
  BOOST_REQUIRE(variants.size() == 2);
  // First variant is without any dish elements
  BOOST_REQUIRE(variants.front()->elements.size() == 0);
  // Second variant is the one with dish elements
  BOOST_REQUIRE(variants.back()->elements.size() == 1);
  
  // Cleaning
  for (Dish * dish : variants)
    delete dish;
}

BOOST_AUTO_TEST_SUITE_END() // dishes