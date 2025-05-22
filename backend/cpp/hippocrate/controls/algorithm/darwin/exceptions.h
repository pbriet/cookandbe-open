#ifndef ALGORITHM_DARWIN_EXCEPTIONS_H_
# define ALGORITHM_DARWIN_EXCEPTIONS_H_

# include "hippocrate/tools/exception.h"

class DarwinCriticalException : public hp::Exception
{
    public:
      DarwinCriticalException(const hp::Exception::Infos & infos, std::string _message) : hp::Exception(infos), message(_message) {}

      std::string message;
      virtual const char* what() const throw() { return "Critical darwin error"; }
};


class DarwinConfigMustBeReadyException : public hp::Exception
{
    public:
      DarwinConfigMustBeReadyException(const hp::Exception::Infos & infos) : hp::Exception(infos) {}
      virtual const char* what() const throw() { return "Darwin config is not ready"; }
};

#endif  // !ALGORITHM_DARWIN_EXCEPTIONS_H_