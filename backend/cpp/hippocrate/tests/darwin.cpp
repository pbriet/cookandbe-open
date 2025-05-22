#include <boost/test/unit_test.hpp>
#include <boost/test/output_test_stream.hpp>

#include "hippocrate/controls/algorithm/darwin/config.h"

BOOST_AUTO_TEST_SUITE(config_suite)


BOOST_AUTO_TEST_CASE(load_correct_config)
{
  DarwinConfig::load("./fixtures/darwin_config_sample.yml");
  BOOST_REQUIRE(DarwinConfig::is_loaded());
  BOOST_REQUIRE(DarwinConfig::is_loaded(true));
  BOOST_CHECK_EQUAL(DarwinConfig::get<long>("nb_generations"), 10);
  BOOST_CHECK_CLOSE(DarwinConfig::get<double>("mutation_rate"), 0.5, 10e-3);
  BOOST_CHECK_THROW(DarwinConfig::get<double>("mutaaaation_rate"), DarwinConfigException);
  DarwinConfig::reset();
  BOOST_REQUIRE(!DarwinConfig::is_loaded());
  BOOST_REQUIRE(!DarwinConfig::is_loaded(true));
  BOOST_CHECK_THROW(DarwinConfig::get<double>("mutation_rate"), DarwinConfigException);
}


BOOST_AUTO_TEST_CASE(load_incomplete_config)
{
  DarwinConfig::load("./fixtures/darwin_config_incomplete.yml");
  BOOST_REQUIRE(DarwinConfig::is_loaded());
  BOOST_REQUIRE(!DarwinConfig::is_loaded(true));
}

BOOST_AUTO_TEST_CASE(load_invalid_config)
{
  BOOST_CHECK_THROW(DarwinConfig::load("./fixtures/darwin_config_invalid.yml"), DarwinConfigException);
}

BOOST_AUTO_TEST_SUITE_END()