
#include <ostream>

#include "hippocrate/tools/print.h"
#include "hippocrate/tools/debug.h"
#include "hippocrate/tools/exception.h"

template <typename T>
struct TemplatedTestException : public hp::Exception
{
    explicit    TemplatedTestException(const hp::Exception::Infos & infos, const T & t) : hp::Exception(infos), data(t) {}
    virtual     ~TemplatedTestException() {}
    virtual std::ostream &      custom(std::ostream & output) const override { return print(output, this->data.text()); }
    
    T           data;
};

struct ExceptionTestClass
{    
    static const std::string &      text() { static std::string t = "May the force be with you"; return t; }
};
