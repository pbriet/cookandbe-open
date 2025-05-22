#include <boost/test/unit_test.hpp>
#include "hippocrate/tests/solution.h"

BOOST_FIXTURE_TEST_SUITE(dishdomain_aggregated, AggregatedDishesFixture)
/*
 * Test the creation of dish domains
 */
BOOST_AUTO_TEST_CASE(simple_aggregated)
{
  /*
   * Checking that the domain for an aggregated dish has two options :
   * one containing two lists of recipes  (dishtype1, dishtype2)
   * one containing one list of recipes (dishtype_agg)
   */
  // There is one dish, so only one domain
  BOOST_REQUIRE(this->di.domains.size() == 1);

  DishDomainOptions * options = this->di.domains.at(this->dish->dish_id);

  BOOST_CHECK_EQUAL(options->dish_id, this->dish->dish_id);

  // The 2 options we are looking for
  BOOST_REQUIRE(options->options.size() == 2);

  DishDomain * splitted_domain = options->options[0];
  // 2 indexes, one with dishtype1 recipes, one with dishtype2 recipes
  BOOST_REQUIRE(splitted_domain->indexes.size() == 2);
  
  BOOST_REQUIRE(splitted_domain->indexes[0]->recipe_ids.size() == 1);
  BOOST_CHECK_EQUAL(splitted_domain->indexes[0]->recipe_ids[0], this->recipe1.recipe_id);
  
  BOOST_REQUIRE(splitted_domain->indexes[1]->recipe_ids.size() == 1);
  BOOST_CHECK_EQUAL(splitted_domain->indexes[1]->recipe_ids[0], this->recipe2.recipe_id);

  // Checking the structure of the dish variant (should be a copy of the original dish)
  BOOST_REQUIRE(splitted_domain->dish_variant->elements.size() == 2);
  BOOST_CHECK_EQUAL(splitted_domain->dish_variant->elements.front()->dish_type_id, 1);
  BOOST_CHECK_EQUAL(splitted_domain->dish_variant->elements.back()->dish_type_id, 2);

  DishDomain * agg_domain = options->options[1];
  // 1 index, with dishtype_agg recipes
  BOOST_REQUIRE(agg_domain->indexes.size() == 1);

  BOOST_REQUIRE(agg_domain->indexes[0]->recipe_ids.size() == 1);
  BOOST_CHECK_EQUAL(agg_domain->indexes[0]->recipe_ids[0], this->recipe_agg.recipe_id);

  // Checking the structure of the dish variant (should be an aggregated dish)
  BOOST_REQUIRE(agg_domain->dish_variant->elements.size() == 1);
  BOOST_CHECK_EQUAL(agg_domain->dish_variant->elements.front()->dish_type_id, 3);
}



BOOST_AUTO_TEST_CASE(domain_from_solution)
{
  /*
   * Checking domain_from_solution method
   */
  DishDomainOptions * options = this->di.domains.at(this->dish->dish_id);
  BOOST_REQUIRE(options->options.size() == 2);

  Solution splitted_solution(this->problem);
  splitted_solution.set_recipe_list(1, { &(this->recipe1), &(this->recipe2) });
  
  BOOST_CHECK_EQUAL(options->domain_from_solution(&splitted_solution),
                    options->options[0]);
    
  Solution aggregated_solution(this->problem);
  aggregated_solution.set_recipe_list(1, { &(this->recipe_agg) });

  BOOST_CHECK_EQUAL(options->domain_from_solution(&aggregated_solution),
                    options->options[1]);
}

BOOST_AUTO_TEST_SUITE_END() // dishdomain_aggregated