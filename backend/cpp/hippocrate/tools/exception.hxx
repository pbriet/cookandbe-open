#ifndef HIPPOCRATE_TOOLS_EXCEPTION_HXX
# define HIPPOCRATE_TOOLS_EXCEPTION_HXX

# include "hippocrate/tools/exception.h"

namespace hp {
  template <typename ... Args>
  InternalError::InternalError(const Infos & infos, const Args & ... args)
      : Exception(infos), _message(sprint(args ...))
  {}
} // ::hp

#endif // HIPPOCRATE_TOOLS_EXCEPTION_HXX
