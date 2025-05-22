#include <boost/python/def.hpp>
#include <vector>
#include <string>
#include <map>
#include <set>

#include "wrapstd.h"

void export_std()
{
  using namespace boost::python;

  class_< std::map<const std::string, long> >("StrToLongHash")
      .def(map_indexing_suite< std::map<const std::string, long> >() );

  class_< std::map<long, double> >("LongToDoubleHash")
      .def(map_indexing_suite< std::map<long, double> >() );

  class_< std::map<long, long> >("LongToLongHash")
      .def(map_indexing_suite< std::map<long, long> >() );
      
  class_< std::vector<double> >("DoubleVector")
      .def(vector_indexing_suite< std::vector<double> >() );

  class_< std::map<long, std::vector<long> > >("LongToLongVectorHash")
      .def(map_indexing_suite< std::map<long, vector_indexing_suite<std::vector<long> > > >() );
}
