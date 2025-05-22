
# include <boost/exception/info.hpp>
# include <boost/exception/get_error_info.hpp>
# include <boost/format.hpp>
# include <cxxabi.h>
# include <execinfo.h>

# include "hippocrate/tools/traceback.h"

using namespace hp;

Traceback::Traceback()
    : trace()
{
    Traceback::generate(this->trace);
}

// Demangle a C++ traceback symbol
std::string
Traceback::demangle(const char * symbol) {
  size_t    size;
  int       status;
  char      temp[128];
  char*     demangled;

  //first, try to demangle a C++ name
  if (1 == sscanf(symbol, "%*[^(]%*[^_]%127[^)+]", temp)) {
    if (nullptr != (demangled = abi::__cxa_demangle(temp, nullptr, &size, &status))) {
      std::string result(demangled);
      free(demangled);
      return result;
    }
  }
  //if that didn't work, try to get a regular c symbol
  if (1 == sscanf(symbol, "%127s", temp)) {
    return temp;
  }
 
  //if all else fails, just return the symbol
  return symbol;
}

void
Traceback::generate(Traceback::Trace & trace)
{    
    void    * addresses[MAX_FRAMES];
    int     size;
    char    ** symbols = nullptr;

    size    = backtrace(addresses, MAX_FRAMES);
    symbols = backtrace_symbols(addresses, size);
    for (int i = 0; i < size; ++i) {
        trace.push_back(demangle(symbols[i]));
    }
    free(symbols);
}

std::string
Traceback::str(long max_lines, const std::string & separator) {
    Traceback::Trace    trace;
    std::string         res;
    
    Traceback::generate(trace);
    for (std::string line : trace)
    {
        if (max_lines-- == 0)
        {
            res += "..." + separator;
            break;
        }
        res += line + separator;
    }
    return res;
}

std::string
Traceback::format(size_t first, const std::string & separator) const {
    std::string         res;
    
    for (size_t i = 0; i < this->trace.size(); ++i)
        if (i >= first)
            res += (boost::format("%1%.%|4t|%2%%3%") % (i - first + 1) % this->trace[i] % separator).str();
    return res;
}
