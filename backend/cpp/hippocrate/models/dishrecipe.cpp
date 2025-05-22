#include <boost/python/module.hpp>
#include <boost/python/def.hpp>

#include "hippocrate/wrapstd.h"
#include "hippocrate/models/dishrecipe.h"

void export_dishrecipe()
{
  using namespace boost::python;

  class_<DishRecipe, DishRecipe*>("DishRecipe", no_init)
    .def_readonly("dish_id",          &DishRecipe::dish_id)
    .def_readonly("recipe",           &DishRecipe::recipe)
    .def_readonly("ratio",            &DishRecipe::ratio)
    .def_readonly("fully_filtered",   &DishRecipe::fully_filtered)
    .def_readonly("order",            &DishRecipe::order);
}


