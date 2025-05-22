
#include <boost/python.hpp>
#include <iostream>

#include "hippocrate/tools/random.h"


void    RandomGenerator::reinit_seed(long value)
{
  RandomGenerator::getInstance().random_engine.seed(value);
  RandomGenerator::getInstance().norm_distrib.reset();
}

double  RandomGenerator::get_norm_distrib_value(double gauss_center, double stddev)
{
  return RandomGenerator::getInstance().norm_distrib(RandomGenerator::getInstance().random_engine,
                                                     std::normal_distribution<double>::param_type(gauss_center, stddev));
}

long RandomGenerator::rand()
{
  return RandomGenerator::getInstance().random_engine();
}

/*
 * Returns true if a number randomly picked between 0 and 1 is below the given number
 */
bool RandomGenerator::in_percentage(double percentage)
{
  ASSERT(percentage >= 0 && percentage <= 1, "Percentage should be between 0 and 1");
  return RandomGenerator::rand() % 100001 <= 100000*percentage;
}

void export_tools()
{
  boost::python::def("set_random_seed", RandomGenerator::getInstance().reinit_seed);
}