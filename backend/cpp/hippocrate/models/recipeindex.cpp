
#include <boost/python.hpp>
#include <boost/python/list.hpp>
#include <boost/python/dict.hpp>
#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/return_value_policy.hpp>
#include <boost/python/reference_existing_object.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include <iostream>
#include <algorithm>
#include <math.h>

#include "hippocrate/wrapstd.h"
#include "hippocrate/tools/random.h"
#include "hippocrate/tools/container.h"
#include "hippocrate/models/recipeindex.h"
#include "hippocrate/models/recipe.h"

void   DetailedRecipeIndex::add_recipe_data(RecipeData *r)
{
  this->all_recipes.push_back(r);
  this->recipe_ids.push_back(r->recipe_id);
}

/*
 * Calculates all the indexes
 */
void    DetailedRecipeIndex::compute_indexes()
{
  this->init_food_idx();
  this->init_cooking_method_idx();
  this->init_data_idx();
  std::sort(this->recipe_ids.begin(), this->recipe_ids.end());
}

/*
 * Indexes recipes per food
 */
void    DetailedRecipeIndex::init_food_idx()
{
  long food_id;
  for(auto rdata: this->all_recipes)
    for(auto food_grams: rdata->foods)
    {
      food_id = food_grams.first;
      hp::default_get(this->per_food, food_id).push_back(rdata);
    }
}

/*
 * Indexes recipes per cooking method
 */
void    DetailedRecipeIndex::init_cooking_method_idx()
{
  for(auto rdata: this->all_recipes)
    for(long cooking_method_id: rdata->cooking_method_ids)
      hp::default_get(this->per_cooking_method, cooking_method_id).push_back(rdata);
}

/*
 * Prepares internal indexes for data
 *
 * this->_data_sorted_values:       {data_id -> list of sorted values}
 * this->_data_sorted_recipes:      {data_id -> list of corresponding recipes}
 */
void    DetailedRecipeIndex::init_data_idx()
{
  long data_id;
  long data_value;
  // First, retrieving nutrient values and related recipes unsorted
  for(auto rdata: this->all_recipes)
    for(auto data_id: rdata->defined_data_ids)
    {
      // WARNING: the ratio of 1.0 is required to initialize the index with standard proportions
      data_value = rdata->get_data(data_id, 1.0);
      hp::default_get(this->_data_sorted_values, data_id).push_back(data_value);
      hp::default_get(this->_data_sorted_recipes, data_id).push_back(rdata);
    }

  // Now, for each data, sorting recipes by values
  for (std::map<long, RecipeDataVector>::const_iterator it = this->_data_sorted_recipes.begin();
       it != this->_data_sorted_recipes.end(); ++it)
  {
    data_id = it->first;
    hp::sort_from_first_vector(this->_data_sorted_values[data_id], this->_data_sorted_recipes[data_id]);
  }
}


bool
DetailedRecipeIndex::has_recipe(long recipe_id) const
{
  return std::binary_search(this->recipe_ids.begin(), this->recipe_ids.end(), recipe_id);
}

/*
 * Returns a random recipe, optionally with some food or with
 * a specific cooking_method
 */
RecipeData *DetailedRecipeIndex::random_recipe()
{
  ASSERT(this->all_recipes.size(), "random_recipe: there is no recipe in DetailedRecipeIndex!");
  size_t index = RandomGenerator::rand() % this->all_recipes.size();
  ASSERT(index >= 0 || index < this->all_recipes.size(), "random_recipe: index out of bound");
  return this->all_recipes[index];
}



/*
 * Return _one_ random recipe for which the data value for data_id is close to target_value
 *
 * It uses a random number from a normal (gaussian) distribution, so the probability having a number close to target_value is high.
 *
 * @param variance: maximum difference to the target_value that could be accepted. If negative, any value could be picked.
 *
 * Warning: variance is the maximum difference with the random value that is generated.
 *          then we select the closest existing value in the recipes, that might be even more different.
 *
 * Note: Reducing variance increases the probability of having values closer to target_value.
 */
RecipeData *DetailedRecipeIndex::recipe_data_normal(long data_id, double target_value, double variance = -1.0)
{
  if (this->_data_sorted_values.find(data_id) == this->_data_sorted_values.end())
    return 0; // No recipe with this data
  
  const RecipeDataValuesVector &data_values = this->_data_sorted_values[data_id];

  // the width of the gaussian is max(target_value - min, max - target_value)
  double gaussian_width = std::max(target_value - data_values.front(), data_values.back() - target_value);

  if (variance < 0.0)
      variance = gaussian_width;  // the gaussian variance is covering all the possible values

  // standard deviation, applying scale to reduce the width (thus the probability of being close to target)
  double std_dev = sqrt(variance);

  // middle of the gaussion is target_value
  double gaussian_loc = target_value;

  // Random data value (with normal probability centered on target_value)
  double random_data_value = RandomGenerator::get_norm_distrib_value(gaussian_loc, std_dev);

  // Finally returning the recipe the closest to this value
  return this->get_closest_recipe(data_id, random_data_value);
}

/*
** Détruit toutes les RecipeData stockée dans l'index et vide tous les conteneurs.
** Attention: cette méthode n'est pas à appeler dans le destruteur, car en principe
** les RecipeData ne sont pas à la charge de l'index.
*/
void
DetailedRecipeIndex::clear()
{
    // for (RecipeData * recipe : this->all_recipes)
        // delete recipe;
    this->all_recipes.clear();
    this->recipe_ids.clear();
    this->per_food.clear();
    this->per_cooking_method.clear();
    this->_data_sorted_values.clear();
    this->_data_sorted_recipes.clear();
}

/*
 * Returns the recipe which is the closest to a given value for a given nutrient
 */
RecipeData *DetailedRecipeIndex::get_closest_recipe(long nutri_id, double random_nutri_value)
{
  const RecipeDataValuesVector &nutrient_values = this->_data_sorted_values[nutri_id];

  // Searching in vector where is the closest value  (lower_bound uses binary search)
  RecipeDataValuesVector::const_iterator it = std::lower_bound(nutrient_values.begin(),
                                                             nutrient_values.end(),
                                                             random_nutri_value);

  // special case when random value is bigger than any existing
  if (it == nutrient_values.end())
      it--;
  else if (it != nutrient_values.begin() && random_nutri_value - *(it - 1) < *it - random_nutri_value)
  {
    // The value before insertion point is closer to the value
    it--;
  }

  // Let's check if there is one or more recipe with the same amount of nutrient
  RecipeDataValuesVector::const_iterator min_it = it;
  RecipeDataValuesVector::const_iterator max_it = it;
  
  while (max_it != (nutrient_values.end() - 1) && *(max_it + 1) == *max_it)
      max_it++;
  while (min_it != nutrient_values.begin() && *(min_it - 1) == *min_it)
      min_it--;

  uint result_i;
  
  if (min_it != max_it)
    // Multiple recipes with same value
    // Take randomly one of the recipes with this value
     result_i = min_it - nutrient_values.begin() + RandomGenerator::rand() % (max_it - min_it + 1);
  else
     result_i = it - nutrient_values.begin();
  
  return this->_data_sorted_recipes[nutri_id][result_i];
}


    void                                add_recipes(RecipeList &recipe_data_vector,
                                                    bool auto_build_index = false);
    void                                add_recipe(RecipeData *r);
    
    void                                build_index();

/*
 * Add recipes in the index
 */
void
RecipeIndex::add_recipes(RecipeList &recipe_data_vector,
                         bool auto_build_index)
{
  for(auto rdata: recipe_data_vector)
    this->add_recipe(rdata);
  if (auto_build_index)
    this->build_index();
}

/*
 * Adds one recipe in the index
 */
void
RecipeIndex::add_recipe(RecipeData *rdata)
{
  this->recipes[rdata->recipe_id] = rdata;
  this->global_index.add_recipe_data(rdata);
}

/*
 * Initialize the indexes (fast access to the recipes)
 */
void
RecipeIndex::build_index()
{
  this->global_index.compute_indexes();
}

/*
 * Returns true if the index isn't empty
 */
bool
RecipeIndex::ready() const
{
  return this->recipes.size() > 0;
}

/*
 * Empty the index
 */
void
RecipeIndex::reset()
{
  this->recipes.clear();
}

/*
 * Returns a copy of the recipe index
 */
RecipeIndex *
RecipeIndex::copy() const
{
  RecipeIndex * res = new RecipeIndex();
  // Copying the map of recipes
  res->recipes = this->recipes;
  return res;
}

/*
 * Returns a python dictionnary equivalent of recipes
 */
boost::python::dict
RecipeIndex::get_recipes() const
{
  boost::python::dict res;
  for(auto r_pair: this->recipes)
    res[r_pair.first] = r_pair.second;
  return res;
}

RecipeData*     py_recipe_by_id(const RecipeIndex *ri, long i)
{
  if (!(hp::has_key(ri->recipes, i)))
  {
    PyErr_SetString(PyExc_KeyError,"Map key not found");
    throw_error_already_set();
    return 0;
  }
  return ri->recipes.at(i);
}

// Activating default arguments for add_recipes
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(add_recipes_default_args, add_recipes, 1, 2);


void export_dish_type_index()
{
  using namespace boost::python;

  class_< RecipeList >("RecipeDataVector")
      .def(vector_indexing_suite< RecipeList >() );

  class_< std::map<long, RecipeList> >("IntToRecipeDataVectorHash")
      .def(map_indexing_suite< std::map<long, RecipeList> >() );

  class_< DetailedRecipeIndex::RecipeDataValuesMap >("RecipeDataValuesMap")
      .def(map_indexing_suite< DetailedRecipeIndex::RecipeDataValuesMap >() );

  class_<DetailedRecipeIndex, DetailedRecipeIndex*>("DetailedRecipeIndex",       init<>())
    .def_readwrite("all_recipes",              &DetailedRecipeIndex::all_recipes)
    .def_readwrite("per_food",                 &DetailedRecipeIndex::per_food)
    .def_readwrite("per_cooking_method",       &DetailedRecipeIndex::per_cooking_method)
    .def_readwrite("_data_sorted_values",  &DetailedRecipeIndex::_data_sorted_values)
    .def_readwrite("_data_sorted_recipes", &DetailedRecipeIndex::_data_sorted_recipes)
    .def("add_recipe_data",         &DetailedRecipeIndex::add_recipe_data)
    .def("random_recipe",           &DetailedRecipeIndex::random_recipe, return_value_policy<reference_existing_object>())
    .def("recipe_data_normal",     &DetailedRecipeIndex::recipe_data_normal, return_value_policy<reference_existing_object>());

  class_<RecipeIndex>("RecipeIndex",       init<>())
    .def("get_recipes",      &RecipeIndex::get_recipes)
    .def("add_recipes",      &RecipeIndex::add_recipes, add_recipes_default_args())
    .def("add_recipe",       &RecipeIndex::add_recipe)
    .def("build_index",      &RecipeIndex::build_index)
    .def("ready",            &RecipeIndex::ready)
    .def("reset",            &RecipeIndex::reset)
    .def("copy",             &RecipeIndex::copy, return_value_policy<manage_new_object>())
    .def("__getitem__",      &py_recipe_by_id, return_value_policy<reference_existing_object>());
    
}


