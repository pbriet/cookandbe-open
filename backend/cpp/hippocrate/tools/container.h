#ifndef HIPPOCRATE_TOOLS_CONTAINER_H_
# define HIPPOCRATE_TOOLS_CONTAINER_H_

# include <set>
# include <map>
# include <list>
# include <vector>

namespace hp {

/*
* Sort v1 and apply the same order to v2  (v1.size() should be equal to v2.size())
* Python equivalent of:
*   ids = numpy.argsort(v1)
*   v1, v2 = v1[ids], v2[ids]
*/
template <typename elements_type1, typename elements_type2>
void            sort_from_first_vector(std::vector<elements_type1> &v1, std::vector<elements_type2> &v2);

/*
 * Returns a concatenation of 2 containers
 */
template <typename CONTAINER>
CONTAINER       concatenate(const CONTAINER &c1, const CONTAINER &c2);

/*
 * Returns true if value in container
 */
template <typename CONTAINER>
bool            in_array(const CONTAINER & container, typename CONTAINER::value_type value);

/*
 * Remove an element from a container
 */
template <typename CONTAINER>
void            remove_from(CONTAINER & container, typename CONTAINER::value_type value, bool raise_if_missing = true);

/*
 * Returns true if value in container (sorted)
 */
template <typename CONTAINER>
bool            in_array_sorted(const CONTAINER & container, typename CONTAINER::value_type value);


/*
 * Returns true if there is at least one element in both containers
 */
template <typename CONTAINER1, typename CONTAINER2>
bool            has_in_common(const CONTAINER1 & c1, const CONTAINER2 & c2);

/*
 * Returns true if a set/list/vector is included into another
 */
template <typename CONTAINER1, typename CONTAINER2>
bool            is_included(const CONTAINER1 & main, const CONTAINER2 & sub);

/*
 * Returns the index of the first occurence of the element in the container.
 * If there is no such element, raise an ValueError.
 */
template <typename CONTAINER, typename VALUE>
unsigned int    get_index(const CONTAINER & v, const VALUE & value);

/*
Returns the sum of all container elements
*/
template <typename CONTAINER>
typename CONTAINER::value_type      sum(const CONTAINER & v);

/*
  * Equivalent of defaultdict.get
  * With mapped_type being a constructable type (constructor with no arguments)
  */
template <typename T>
typename T::mapped_type &default_get(T &dict, typename T::key_type key);

/*
 * Returns true if key is in map
 */
template <typename CONTAINER>
bool            has_key(const CONTAINER & container, typename CONTAINER::key_type key);

/*
 * Returns true if key is in map
 */
template <typename CONTAINER>
CONTAINER       intersect(const CONTAINER & c1, const CONTAINER & c2);


} // !hp

# include "hippocrate/tools/container.hxx"

#endif // HIPPOCRATE_TOOLS_CONTAINER_H_