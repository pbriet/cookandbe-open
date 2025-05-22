#ifndef WRAP_STD_HXX_
# define WRAP_STD_HXX_

# include<boost/python/list.hpp>
# include "hippocrate/tools/debug.h"
  
using namespace boost::python;


# define BOOST_WRAP_MAP_READONLY_OBJECT_KEY(map_class, class_name) \
  class_< map_class >(class_name) \
    .def("__len__", &map_class::size) \
    .def("__getitem__", &map_item<map_class::key_type,map_class::mapped_type,map_class::key_compare>().get, return_value_policy<copy_const_reference>() ) \
    .def("clear", &map_class::clear) \
    .def("__contains__", &map_item<map_class::key_type,map_class::mapped_type,map_class::key_compare>().in) \
    .def("has_key", &map_item<map_class::key_type,map_class::mapped_type,map_class::key_compare>().in) \
    .def("keys", &map_item<map_class::key_type,map_class::mapped_type,map_class::key_compare>().keys) \
    .def("values", &map_item<map_class::key_type,map_class::mapped_type,map_class::key_compare>().values)

/*
** Copied from https://wiki.python.org/moin/boost.python/HowTo#std::C.2B-.2B-_container
*/
template<class Key, class Val, class Compare>
struct map_item
{
    typedef std::map<Key,Val,Compare> Map;

    static const Val& get(Map const& self, const Key idx) {
      if( self.find(idx) != self.end() ) return self.at(idx);
      PyErr_SetString(PyExc_KeyError,"Map key not found");
      throw_error_already_set();
      ASSERT(false, "should not be here");
      return self.at(idx); // Just to avoid warnings "method not returning a value"
    }

    static void set(Map& self, const Key idx, const Val val) { self[idx]=val; }

    static void del(Map& self, const Key n) { self.erase(n); }

    static bool in(Map const& self, const Key n) { return self.find(n) != self.end(); }

    static list keys(Map const& self)
    {
        list t;
        for(typename Map::const_iterator it=self.begin(); it!=self.end(); ++it)
            t.append(boost::ref(it->first));
        return t;
    }
    static list values(Map const& self)
    {
        list t;
        for(typename Map::const_iterator it=self.begin(); it!=self.end(); ++it)
            t.append(it->second);
        return t;
    }
};

#endif