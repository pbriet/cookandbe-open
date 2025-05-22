#ifndef HIPPOCRATE_TOOLS_ITER_HXX_
# define HIPPOCRATE_TOOLS_ITER_HXX_

template <typename T>
void  hp::CombinationIterator<T>::init()
{
  if (!(this->range_k))
    this->_current_k = this->k;
  else
    this->_current_k = 1;

  this->init_with_new_k();
}

/*
 * Initialize the first combination of C(n, current_k)
 */
template <typename T>
void hp::CombinationIterator<T>::init_with_new_k()
{
  ASSERT(this->_current_k <= this->possible_values.size(), "Combination of K elements over N, with K > N");

  // Initialize the first value with the first elements
  this->current_indexes.resize(this->_current_k);
  for (uint i = 0; i < this->_current_k; i++)
    this->current_indexes[i] = i;
}

/*
 * Returns current value
 */
template <typename T>
std::vector<T>  hp::CombinationIterator<T>::value()
{
  std::vector<T> res(this->_current_k);
  for (uint i = 0; i < this->_current_k; i ++)
    res[i] = this->possible_values[this->current_indexes[i]];
  return res;
}

/*
 * Move to the next combination
 * Returns false if there is no other
 */
template <typename T>
bool  hp::CombinationIterator<T>::next()
{
  for (int i = this->_current_k - 1; i >= 0; i--)
  {
    if (this->current_indexes[i] < this->possible_values.size() - this->_current_k + i)
    {
      this->current_indexes[i]++;
      for (uint j = i + 1; j < this->_current_k; j++)
        this->current_indexes[j] = this->current_indexes[j - 1] + 1;
      return true;
    }
  }
  if (!(this->range_k) || (this->_current_k == this->k))
    return false; // the end - no more iteration
  // New value for K
  this->_current_k++;
  this->init_with_new_k();
  return true;
}


#endif // HIPPOCRATE_TOOLS_ITER_HXX_