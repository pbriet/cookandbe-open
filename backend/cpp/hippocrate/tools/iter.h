#ifndef HIPPOCRATE_TOOLS_ITER_H_
# define HIPPOCRATE_TOOLS_ITER_H_

namespace hp {

  template <typename T>
  class CombinationIterator
  {
  public:
    CombinationIterator(std::vector<T> _possible_values, uint _k, bool _range_k = false) :
        possible_values(_possible_values), k(_k), range_k(_range_k) { this->init(); }

    CombinationIterator(std::vector<T> _possible_values, bool _range_k = false) :
        CombinationIterator(_possible_values, _possible_values.size(), _range_k) {}
    
    std::vector<T>    possible_values; // List of values
    uint              k; // C(n, k)
    bool              range_k;  // if true, use different values for k (from 1 to k)
    std::vector<uint> current_indexes;

    bool              next();
    std::vector<T>    value();

  private:
    uint              _current_k;
    void              init();
    void              init_with_new_k();
  };

} // !hp

# include "hippocrate/tools/iter.hxx"

#endif // HIPPOCRATE_TOOLS_ITER_H_