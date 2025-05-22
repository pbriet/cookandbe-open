#ifndef WRAP_STD_H_
  #define WRAP_STD_H_
  
  #include <boost/python/suite/indexing/vector_indexing_suite.hpp>
  #include <boost/python/suite/indexing/map_indexing_suite.hpp>

  // Wraps STD-lib objects
  void export_std();

  #include "wrapstd.hxx"
  
#endif