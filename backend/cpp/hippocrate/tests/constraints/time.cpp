
#include <boost/test/unit_test.hpp>

#include "hippocrate/controls/algorithm/darwin/darwin.h"

#include "hippocrate/tests/constraints/time.h"

#include "hippocrate/models/constraints/time.h"
#include "hippocrate/models/dishindex.h"
#include "hippocrate/models/solution.h"
#include "hippocrate/models/problem.h"

BOOST_FIXTURE_TEST_SUITE(TimeConstraintSuite, TimeConstraintFixture)

BOOST_AUTO_TEST_CASE(empty)
{
    this->initialize();
    // Initializing TimeConstraint
    TimeConstraint          constraint1(this->cost_per_minute);
    this->problem->add_constraint(& constraint1);
    this->build_solution();
    BOOST_CHECK_EQUAL(this->get_score_total(*(this->solution)), 0);
}


BOOST_AUTO_TEST_CASE(equal)
{
    // Equal to limit
    this->initialize();
    TimeConstraint          constraint2(this->cost_per_minute);
    constraint2.add_meal_time_limit(this->meal_id, 40, 60, 10); // 2 dishes per meal
    this->problem->add_constraint(& constraint2);
    this->build_solution();
    BOOST_CHECK_EQUAL(this->get_score_total(*(this->solution)), 0);
}


BOOST_AUTO_TEST_CASE(under)
{
    // Under limit
    this->initialize();
    TimeConstraint          constraint3(this->cost_per_minute);
    constraint3.add_meal_time_limit(this->meal_id, 50, 100, 20);
    this->problem->add_constraint(& constraint3);
    this->build_solution();
    BOOST_CHECK_EQUAL(this->get_score_total(*(this->solution)), 0);
}

BOOST_AUTO_TEST_CASE(over)
{
    // Over limit
    this->initialize();
    TimeConstraint          constraint4(this->cost_per_minute);
    constraint4.add_meal_time_limit(this->meal_id, 38, 57, 5);
    this->problem->add_constraint(& constraint4);
    this->build_solution();
    // prep time : 40 minutes > 38  --> cost = 2^2 * 10 = 40
    // cook time : 60 minutes > 57  --> cost = 3^2 * 10 = 90
    // rest time : 10 minutes > 5   --> cost = 5^2 * 10 = 250
    BOOST_CHECK_EQUAL(this->get_score_total(*(this->solution)), 380);
}

BOOST_AUTO_TEST_SUITE_END() // TimeConstraintSuite
