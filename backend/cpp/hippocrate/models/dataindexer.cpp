#include <boost/python.hpp>
#include "hippocrate/models/dataindexer.h"

#include "hippocrate/wrapstd.h"
#include "hippocrate/tools/container.h"

RecipeDataIndexer &   RecipeDataIndexer::instance = *RecipeDataIndexer::get_instance();

RecipeDataIndexer *
RecipeDataIndexer::get_instance() {
  static RecipeDataIndexer obj;

  return &obj;
}

void
RecipeDataIndexer::add_to_index(const std::string &key)
{
  if (hp::has_key(this->data_key_to_id, key))
    RAISE(hp::InternalError, sprint("Key already added : ", key));
  this->data_key_to_id[key] = this->max_id;
  this->max_id++;
}

void
RecipeDataIndexer::reset()
{
  this->max_id = 0;
  this->data_key_to_id.clear();
}


void export_data_indexer()
{
  class_<RecipeDataIndexer, RecipeDataIndexer*, boost::noncopyable>("RecipeDataIndexer", no_init)
    .def("reset",                         &RecipeDataIndexer::reset)
    .def("add_to_index",                  &RecipeDataIndexer::add_to_index)
    .def("id_from_key",                   &RecipeDataIndexer::id_from_key)
    .def("getInstance",                   &RecipeDataIndexer::get_instance, return_value_policy<reference_existing_object>())
    .def("nb_indexed",                    &RecipeDataIndexer::nb_indexed);
}
