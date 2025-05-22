#ifndef HIPPOCRATE_TOOLS_MATH_H_
# define HIPPOCRATE_TOOLS_MATH_H_

# include "hippocrate/tools/exception.h"

namespace hp {
  inline long   mod(long number, long modulo)
  {
    #ifdef DEBUG
    if (!modulo)
        RAISE(ArithmeticalError, "modulo 0 detected");
    #endif // DEBUG
    return std::div(number, modulo).rem;
  }

  inline int    mod(int number, int modulo)
  {
    #ifdef DEBUG
    if (!modulo)
        RAISE(ArithmeticalError, "modulo 0 detected");
    #endif // DEBUG
    return std::div(number, modulo).rem;
  }

  // Surcharge de l'opérateur dans le namespace hp
  template <typename T>
  inline T      operator % (const T & number, const T & modulo)
  {
    return hp::mod(number, modulo);
  }
}

#endif // !HIPPOCRATE_TOOLS_MATH_H_