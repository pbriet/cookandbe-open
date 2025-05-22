#ifndef HIPPOCRATE_TOOLS_RANDOM_HXX_
# define HIPPOCRATE_TOOLS_RANDOM_HXX_

# include "hippocrate/tools/debug.h"
# include "hippocrate/tools/random.h"
# include "hippocrate/tools/math.h"

template <typename T>
T RandomGenerator::pick(const std::vector<T> &values)
{
    ASSERT(values.size(), "pick in empty vector");
    return values[hp::mod(RandomGenerator::rand(), values.size())];
}

template <typename T, typename U>
const T &
RandomGenerator::pick_key(const std::map<T, U> &values)
{
    ASSERT(values.size(), "pick key in empty map");
    typename std::map<T, U>::const_iterator  it = values.begin();
    std::advance(it, hp::mod(RandomGenerator::rand(), values.size()));
    return (*it).first;
}

template <typename T, typename U>
const U &
RandomGenerator::pick_value(const std::map<T, U> &values)
{
    ASSERT(values.size(), "pick value in empty map");
    typename std::map<T, U>::const_iterator  it = values.begin();
    std::advance(it, hp::mod(RandomGenerator::rand(), values.size()));
    return (*it).second;
}


template <typename T>
T RandomGenerator::pick_distrib_value(const std::map<T, long> &distrib, long total)
{
  ASSERT(distrib.size(), "pick distrib value in empty map");

  // Imagine that all the values are represented with a barchart
  // random_value is the random point we select on the barchart
  // to see which element we pick
  if (total <= 0)
  {
    total = 0;
    for (auto pair: distrib)
      total += pair.second;
  }
  if (total <= 0)
    return RandomGenerator::pick_key(distrib);
  // Picking a random one
  long random_value = hp::mod(RandomGenerator::rand(), total) + 1;
  long value_aggregated = 0;

  for (auto pair: distrib)
  {
    value_aggregated += pair.second;
    if (value_aggregated >= random_value)
        return pair.first;
  }
  RAISE(hp::InternalError, "definitely shouldn't be here (pick_distrib_value)");
  return distrib.begin()->first;
}


template <typename T>
uint RandomGenerator::pick_distrib_value(const std::vector<T> &distrib, long total)
{
  ASSERT(distrib.size(), "pick distrib value in empty vector");
  if (total <= 0)
  {
    total = 0;
    for (uint i = 0; i < distrib.size(); i++)
      total += distrib[i];
  }
  if (total <= 0)
    return hp::mod(RandomGenerator::rand(), distrib.size());
  // Picking a random one
  long random_value = hp::mod(RandomGenerator::rand(), total) + 1;
  long value_aggregated = 0;
  for (uint i = 0; i < distrib.size(); i++)
  {
    value_aggregated += distrib[i];
    if (value_aggregated >= random_value)
      return i;
  }
  RAISE(hp::InternalError, "definitely shouldn't be here (pick_distrib_value vector)");
  return 0;
}

#endif // HIPPOCRATE_TOOLS_RANDOM_HXX_
