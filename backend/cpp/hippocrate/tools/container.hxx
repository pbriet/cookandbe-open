#ifndef HIPPOCRATE_TOOLS_CONTAINER_HXX_
# define HIPPOCRATE_TOOLS_CONTAINER_HXX_

# include <algorithm>
# include <numeric>

# include "hippocrate/tools/debug.h"
# include "hippocrate/tools/container.h"
# include "hippocrate/tools/exception.h"

/*
* Function of comparison of two pairs, comparing only on first element
*/
template<typename elements_type1, typename elements_type2>
static bool
pair_cmp_first(const std::pair<elements_type1, elements_type2> l,
               const std::pair<elements_type1, elements_type2> r)
{
    return l.first < r.first;
}

template<typename elements_type1, typename elements_type2>
void
hp::sort_from_first_vector(std::vector<elements_type1> &v1, std::vector<elements_type2> &v2)
{
    ASSERT(v1.size() == v2.size(), "different vector sizes (sort_from_first_vector)");
    // First, creating a vector of pairs (value1, index)
    typedef std::pair<elements_type1, uint> PairValueIndex;

    std::vector<PairValueIndex> pair_vector(v1.size());
    for (uint i = 0; i < v1.size(); i++)
      pair_vector[i] = PairValueIndex(v1[i], i);

    // Sorting the vector of pairs on first element (sorted by value1)
    std::sort(pair_vector.begin(), pair_vector.end(), pair_cmp_first<elements_type1, uint>);

    // Altering v1 and v2
    std::vector<elements_type2>  new_v2(v1.size());
    for (uint i = 0; i < pair_vector.size(); i++)
    {
      // v1 is already sorted (first value of pair is v1 value)
      v1[i] = pair_vector[i].first;
      // Creating new v2 vector, sorted the same way v1 is (second value of pair being the index)
      new_v2[i] = v2[pair_vector[i].second];
    }
    v2 = new_v2;
}

// Equivalent of defaultdict.get
// With mapped_type being a constructable type (constructor with no arguments)
template <typename T>
typename T::mapped_type &
hp::default_get(T &dict, typename T::key_type key)
{
    if (!dict.count(key)) { dict[key] = typename T::mapped_type(); }
    return dict[key];
}


template <typename CONTAINER>
bool
hp::in_array(const CONTAINER & container, typename CONTAINER::value_type value)
{
    return std::find(container.begin(), container.end(), value) != container.end();
}

template <typename CONTAINER>
void
hp::remove_from(CONTAINER & container, typename CONTAINER::value_type value, bool raise_if_missing)
{
  auto it = std::find(container.begin(), container.end(), value);
  if (it != container.end())
  {
    container.erase(it);
    return;
  }
  if (raise_if_missing)
    RAISE(hp::InternalError, "remove from: element not in container");
}

template <typename CONTAINER>
bool
hp::in_array_sorted(const CONTAINER & container, typename CONTAINER::value_type value)
{
    ASSERT(std::is_sorted(container.begin(), container.end()), "using in_array_sorted with unsorted arrays");
    auto it = std::lower_bound(container.begin(), container.end(), value);
    if (it == container.end() || *it != value)
      return false;
    return true;
}

template <typename CONTAINER, typename VALUE>
unsigned int
hp::get_index(const CONTAINER & c, const VALUE & value)
{
    typedef hp::ValueError<CONTAINER> ValueError;
    typename CONTAINER::const_iterator  pos = std::find(c.begin(), c.end(), value);

    if (pos == c.end())
        RAISE(ValueError, c, value);
    return (pos - c.begin());
}

/*
 * Does the sum of all container elements
 */
template <typename CONTAINER>
typename CONTAINER::value_type
hp::sum(const CONTAINER & container)
{
  return std::accumulate(container.begin(), container.end(), CONTAINER::value_type());
}

template <typename CONTAINER>
bool
hp::has_key(const CONTAINER & container, typename CONTAINER::key_type key)
{
  return container.find(key) != container.end();
}

/*
 * Returns true if a set is included into another
 */
template <typename CONTAINER1, typename CONTAINER2>
bool
hp::is_included(const CONTAINER1 & main, const CONTAINER2 & sub)
{
  for (auto sub_elt: sub)
    if (std::find(main.begin(), main.end(), sub_elt) == main.end())
      return false;
  return true;
}


/*
 * Returns true if there is at least one element in both containers
 */
template <typename CONTAINER1, typename CONTAINER2>
bool
hp::has_in_common(const CONTAINER1 & c1, const CONTAINER2 & c2)
{
  for (auto elt1: c1)
    if (std::find(c2.begin(), c2.end(), elt1) != c2.end())
      return true;
  return false;
}


/*
 * Returns a concatenation of 2 containers
 */
template <typename CONTAINER>
CONTAINER
hp::concatenate(const CONTAINER &c1, const CONTAINER &c2)
{
  CONTAINER res(c1);
  res.reserve(c1.size() + c2.size());
  res.insert(res.end(), c2.begin(), c2.end());
  return res;
}


/*
 * Returns an intersection of two containers
 */
template <typename CONTAINER>
CONTAINER
hp::intersect(const CONTAINER & c1, const CONTAINER & c2)
{
    CONTAINER res(std::min(c1.size(), c2.size()));
    auto iterator = std::set_intersection(c1.begin(), c1.end(), c2.begin(), c2.end(),
                                          res.begin());
    res.resize(iterator - res.begin());
    return res;
}

#endif // HIPPOCRATE_TOOLS_CONTAINER_HXX_