
#include <boost/test/unit_test.hpp>

#include "hippocrate/controls/algorithm/darwin/darwin.h"
#include "hippocrate/tests/algorithm.h"
#include "hippocrate/models/solution.h"

BOOST_FIXTURE_TEST_SUITE(algorithm_suite, AlgorithmFixture)

BOOST_AUTO_TEST_CASE(base)
{
    this->initialize();
    Solution                        solution(this->problem);
    NutrientConstraint              * constraint = nullptr;
    
    RecipeDataIndexer::instance.add_to_index("toto");
      
    // Evaluating empty solution without constraint
    BOOST_CHECK_THROW(this->problem->eval(&solution), InvalidSolution);
    // Adding constraint to the problem
    constraint = new NutrientConstraint(/* nutrient key */ "toto",
                                        /* min */ -1,
                                        /* max */ 1000,
                                        /*daily_tolerance_min*/ 0,
                                        /*daily_tolerance_max*/ 0,
                                        /* cost_per_percent_out */ 100,
                                        /* create_weekly_constraint */ true);
    this->problem->add_constraint(constraint);
    // Evaluating empty solution with constraint
    BOOST_CHECK_THROW(this->problem->eval(&solution), InvalidSolution);
    delete constraint;
}


BOOST_AUTO_TEST_CASE(darwin)
{
    this->initialize();
    DarwinConfig::load("./fixtures/darwin_config_sample.yml");
    Solution                solution(this->problem);
    DarwinAlgorithm         * algorithm = new DarwinAlgorithm(this->problem);

    solution = algorithm->solve();
    BOOST_CHECK_EQUAL(solution.get_nb_dishes(), this->nbTotalDishes());

    delete algorithm;
}


BOOST_AUTO_TEST_CASE(darwin_with_oriented)
{
    this->initialize();
    DarwinConfig::load("./fixtures/darwin_config_oriented.yml");
    Solution                solution(this->problem);
    DarwinAlgorithm         * algorithm = new DarwinAlgorithm(this->problem);

    solution = algorithm->solve();
    BOOST_CHECK_EQUAL(solution.get_all_recipes().size(), this->nbTotalDishes());

    delete algorithm;
}


BOOST_AUTO_TEST_SUITE_END() // algorithm_suite
