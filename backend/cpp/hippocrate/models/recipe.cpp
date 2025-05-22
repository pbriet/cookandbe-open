#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/overloads.hpp>

#include "hippocrate/wrapstd.h"
#include "hippocrate/models/recipe.h"

/*
 * This file contains the main class RecipeData, which is built from a Recipe,
 *  and contains:
 * A recipe_id
 * The amount of nutrients for 1 portion (calculated from ingredients)
 * dish_type
 * prep_mins
 * ...
 And anything that is required by Hippocrate, in the most minimized way  (these objects are stored in RAM)
*/

RecipeData::RecipeData(long recipe_id) :
  recipe_id(recipe_id)
{
}


/*
 * Add data in the static array (fast access guaranteed)
 * using the DataIndexer to translate <key> into <id>
 */
void
RecipeData::add_data(const std::string &key, double value)
{
  long key_id = RecipeDataIndexer::instance[key];
  this->data[key_id] = value;
  this->defined_data_ids.push_back(key_id);
}


/*
 * From the DataIndexer, allocate a static array of doubles, given the number of keys
 * stored in the indexer
 */
void RecipeData::allocate_data()
{
  long rdi_size = RecipeDataIndexer::instance.nb_indexed();
  if (rdi_size == 0)
    return;
  this->data.resize(rdi_size);
}

double
RecipeData::compute_best_ratio(double target_ratio) const
{
  // TODO: faire le système de calcul de portion de recettes tenant compte des ingrédients discrêts.
  return target_ratio;
}


double
RecipeData::get_data_from_key(const std::string &key, double ratio) const
{
  long data_id = RecipeDataIndexer::instance[key];
  return this->get_data(data_id, ratio);
}

struct recipe_pickle_suite : boost::python::pickle_suite
{
  static
  boost::python::tuple
  getinitargs(RecipeData const& r)
  {
      return boost::python::make_tuple(r.recipe_id);
  }

  static
  boost::python::tuple
  getstate(const RecipeData& r)
  {
    /*
    Bug: make_tuple can't work fine here because of a limitation to 15 arguments...
    It should be possible to patch things up but it seems quite painfull for now.
    See: http://stackoverflow.com/questions/6425178/boost-tuple-increasing-maximum-number-of-elements

    Though C++11 might allow something like that :
      template <class T ...>
      class make_tuple;

    === OLD CODE ===
      using namespace boost::python;
      return make_tuple(r.recipe_id, r.name, r.foods, r.cooking_method_ids, r.dish_type_ids,
                        r.food_tag_ids, r.main_food_tag_ids, r.suggested_food_tag_ids, r.recipe_tag_ids,
                        r.data, r.ustensils, r.internal, r.defined_data_ids);
    */
    boost::python::list   pl;
    pl.append(r.recipe_id);
    pl.append(r.name);
    pl.append(r.status);
    pl.append(r.foods);
    pl.append(r.cooking_method_ids);
    pl.append(r.dish_type_ids);
    pl.append(r.food_tag_ids);
    pl.append(r.main_food_tag_ids);
    pl.append(r.suggested_food_tag_ids);
    pl.append(r.recipe_tag_ids);
    pl.append(r.data);
    pl.append(r.ustensils);
    pl.append(r.internal);
    pl.append(r.nb_ingredients);
    pl.append(r.defined_data_ids);
    return boost::python::tuple(pl);
  }

  static
  void
  setstate(RecipeData& r, boost::python::tuple state)
  {
      using namespace boost::python;
      if (len(state) != 15)
      {
        PyErr_SetObject(PyExc_ValueError,
                        ("expected 14-item tuple in call to __setstate__; got %s"
                          % state).ptr()
            );
        throw_error_already_set();
      }
      r.recipe_id = extract<long>(state[0]);
      r.name = extract<std::wstring>(state[1]);
      r.status = extract<long>(state[2]);
      r.foods = extract<RecipeData::FoodGrams>(state[3]);
      r.cooking_method_ids = extract<RecipeData::IdContainer>(state[4]);
      r.dish_type_ids = extract<RecipeData::IdContainer>(state[5]);
      ASSERT(r.dish_type_ids.size() > 0, "Recipe with 0 dish_types in the cache ! Update the cache and/or fix the recipe issue");
      r.food_tag_ids = extract<RecipeData::IdContainer>(state[6]);
      r.main_food_tag_ids = extract<RecipeData::IdContainer>(state[7]);
      r.suggested_food_tag_ids = extract<RecipeData::IdContainer>(state[8]);
      r.recipe_tag_ids = extract<RecipeData::IdContainer>(state[9]);
      r.data = extract<RecipeData::DataArray>(state[10]);
      if (r.data.size() != RecipeDataIndexer::instance.nb_indexed())
        RAISE(hp::InternalError, sprint("RecipeData Pickle data size differs from indexer. Please clear the cache and restart"));
      r.ustensils = extract<RecipeData::IdContainer>(state[11]);
      r.internal = extract<bool>(state[12]);
      r.nb_ingredients = extract<long>(state[13]);
      r.defined_data_ids = extract<RecipeData::IdContainer>(state[14]);
  }
};

// This function can take 1 or 2 arguments (2nd is optional)
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(data_value_from_key_overload, RecipeData::get_data_from_key, 1, 2)

void export_recipe_data()
{
  using namespace boost::python;


  class_<RecipeData, RecipeData*>("RecipeData", init<long>((arg("recipe_id"))))
    .def_pickle(recipe_pickle_suite())
    .def("add_data",                            &RecipeData::add_data)
    .def("allocate_data",                       &RecipeData::allocate_data)
    .def("get_data_from_key",                   &RecipeData::get_data_from_key, data_value_from_key_overload(args("key", "ratio")))
    .def_readonly("recipe_id",                  &RecipeData::recipe_id)
    .def_readwrite("name",                      &RecipeData::name)
    .def_readwrite("status",                    &RecipeData::status)
    .def_readwrite("foods",                     &RecipeData::foods)
    .def_readwrite("cooking_method_ids",        &RecipeData::cooking_method_ids)
    .def_readwrite("dish_type_ids",             &RecipeData::dish_type_ids)
    .def_readwrite("food_tag_ids",              &RecipeData::food_tag_ids)
    .def_readwrite("main_food_tag_ids",         &RecipeData::main_food_tag_ids)
    .def_readwrite("suggested_food_tag_ids",    &RecipeData::suggested_food_tag_ids)
    .def_readwrite("recipe_tag_ids",            &RecipeData::recipe_tag_ids)
    .def_readwrite("internal",                  &RecipeData::internal)
    .def_readwrite("nb_ingredients",            &RecipeData::nb_ingredients)
    .def_readwrite("perceived_healthy",         &RecipeData::perceived_healthy)
    .def_readonly("ustensils",                  &RecipeData::ustensils)
    .def_readonly("defined_data_ids",           &RecipeData::defined_data_ids);
}


