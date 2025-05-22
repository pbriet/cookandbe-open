
#include <boost/python.hpp>
#include <fstream>
#include <iostream>
#include <algorithm>
#include <stdlib.h>
#include <yaml-cpp/yaml.h>

#include "hippocrate/tools/container.h"
#include "hippocrate/controls/algorithm/darwin/config.h"


const std::vector<std::string> DarwinConfig::string_options_keys = {
    "selection",      // Type of selection
   };

const std::vector<std::string> DarwinConfig::long_options_keys = {
    "population_size",      // Number of plannings
    "nb_generations",       // Number of loops in the algorithm
    "max_lost_generations", // Maximum number of generations without improvement
   };

const std::vector<std::string> DarwinConfig::double_options_keys = {
     "oriented_crossover_rate_start",   // Percentage (float) of oriented crossovers [beginning]
     "oriented_crossover_rate_end",     // Percentage (float) of oriented crossovers [end]
     "oriented_mutation_rate_start",   // Percentage (float) of oriented mutations [beginning]
     "oriented_mutation_rate_end",     // Percentage (float) of oriented mutations [end]
     "crossover_rate",
     "mutation_rate",
     "ratio_change_rate"
   };

bool DarwinConfig::load(std::string  filepath)
{
  DarwinConfig      &darw_config = DarwinConfig::getInstance();
  darw_config.reset();
  // Loading YAML file
  YAML::Node doc = YAML::LoadFile(filepath);
  bool success = true;
  
  for(YAML::const_iterator it=doc.begin(); it!=doc.end(); ++it)
  {
    // Retrieving key, value pairs
    std::string key = it->first.as<std::string>();
    std::string value = it->second.as<std::string>();

    // Storing in double or long values
    if (hp::in_array(darw_config.long_options_keys, key))
      darw_config.long_options[key] = std::stoll(value);
    else if (hp::in_array(darw_config.double_options_keys, key))
      darw_config.double_options[key] = atof(value.c_str());
    else if (hp::in_array(darw_config.string_options_keys, key))
      darw_config.string_options[key] = value;
    else
    {
      success = false;
      throw DarwinConfigException(key);
    }
  }

  return success;
}

/*
 * if fully is True, return True if all options are set
 * if fully is False, return True if at least one option is set
 */
bool DarwinConfig::is_loaded(bool fully)
{
  DarwinConfig      &darw_config = DarwinConfig::getInstance();
  unsigned long expected_size;

  if (fully)
  {
    // Fully means all options are available
    expected_size = darw_config.long_options_keys.size() + darw_config.double_options_keys.size() +\
                    darw_config.string_options_keys.size();
  }
  else
  {
    // At least one config variable is set
    expected_size = 1;
  }
  
  return (darw_config.long_options.size() + darw_config.double_options.size() +\
          darw_config.string_options.size()) >= expected_size;
}


void DarwinConfig::reset()
{
  DarwinConfig      &darw_config = DarwinConfig::getInstance();
  darw_config.long_options.clear();
  darw_config.double_options.clear();
  darw_config.string_options.clear();
}


template<>
long DarwinConfig::get<long>(std::string option)
{
  std::map<std::string, long>  &values = DarwinConfig::getInstance().long_options;
  if (values.count(option))
    return values[option];
  throw DarwinConfigException(option);
}

template<>
std::string DarwinConfig::get<std::string>(std::string option)
{
  std::map<std::string, std::string>  &values = DarwinConfig::getInstance().string_options;
  if (values.count(option))
    return values[option];
  throw DarwinConfigException(option);
}

template<>
double DarwinConfig::get<double>(std::string option)
{
  std::map<std::string, double>  &values = DarwinConfig::getInstance().double_options;
  if (values.count(option))
    return values[option];
  throw DarwinConfigException(option);
}


void export_darwin_config()
{
  using namespace boost::python;
  def("load_darwin_config", &DarwinConfig::load);
}
