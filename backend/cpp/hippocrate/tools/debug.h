#ifndef HIPPOCRATE_TOOLS_DEBUG_H_
# define HIPPOCRATE_TOOLS_DEBUG_H_

# include "hippocrate/tools/traceback.h"
# include "hippocrate/tools/exception.h"

# ifdef DEBUG
#  define ASSERT(expression, ...)                                   \
  do {                                                              \
    auto __assert_result__ = expression;                            \
    if (!(__assert_result__)) {                                     \
      RAISE(hp::AssertionError, #expression, sprint(__VA_ARGS__))   \
    }                                                               \
  } while (false);
# else  // !DEBUG
#  define ASSERT(expression, ...) ;
# endif // DEBUG

#endif // HIPPOCRATE_TOOLS_DEBUG_H_
