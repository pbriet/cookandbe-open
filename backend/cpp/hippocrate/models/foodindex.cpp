
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <algorithm>

#include "hippocrate/tools/container.h"
#include "hippocrate/models/foodindex.h"

void
FoodIndex::add_food(hp::Id food_id, float minimum, FoodIndex::FoodTags & food_tags) {
  if (minimum > 0) {
    this->minimums[food_id] = minimum;
  }
  this->tags[food_id] = food_tags;
}

int
FoodIndex::compute_penalty(hp::Id food_id, long quantity, int cost) const {
  if (quantity == 0 || !hp::has_key(this->minimums, food_id)) {
    return 0;
  }
  
  int food_min = this->minimums.at(food_id);
  
  if (quantity >= food_min) {
    return 0;
  }
  
  float food_delta = food_min - quantity;
  
  return int(cost * (1.0 + float(food_min) / food_delta));
}

void
export_food_index()
{
  using namespace boost::python;

  class_<FoodIndex::FoodTags>("FoodTagList")
      .def(vector_indexing_suite<FoodIndex::FoodTags>());

  class_<FoodIndex>("FoodIndex",  init<>())
    .def("add_food", &FoodIndex::add_food)
    .def("get_tags", &FoodIndex::get_tags)
  ;
}