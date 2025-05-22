
#include <boost/test/output_test_stream.hpp> 

#include "hippocrate/tools/print.h"

std::string             Printer::separator   = " ";
std::string             Printer::empty       = "";
const Printer::NoEnd    Printer::noend       = Printer::NoEnd();

template <>
std::ostream &
Printer::print_element(std::ostream & , std::ostream & new_os, const std::string & )
{ return this->switchStream(new_os); }

template <>
std::ostream &
Printer::print_element(std::ostream & os, std::stringstream & new_os, const std::string & )
{ return this->switchStream(new_os); }

template <>
std::ostream &
Printer::print_element(std::ostream & os, std::ofstream & new_os, const std::string & )
{ return this->switchStream(new_os); }

template <>
std::ostream &
Printer::print_element(std::ostream & os, boost::test_tools::output_test_stream & new_os, const std::string & )
{ return this->switchStream(new_os); }

template <>
std::ostream &
Printer::stream_print(std::ostream & os, const Printer::NoEnd &)
{ return os; }

std::ostream &
print()
{
    return Printer(true).stream_print(std::cout);
}