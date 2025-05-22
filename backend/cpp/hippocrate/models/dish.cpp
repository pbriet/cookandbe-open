#include <boost/python.hpp>
#include "hippocrate/wrapstd.h"
#include "hippocrate/models/dish.h"
#include "hippocrate/models/dishindex.h"
#include "hippocrate/tools/container.h"
#include "hippocrate/tools/iter.h"

/*
 * Merge 2 dish elements into one
 * _nothing_ is done with dish_type_id
 * recipe tags and food tags are gathered together  (union)
 */
void DishElement::merge_with(const DishElement *other)
{
  for (auto recipe_tag_id: other->recipe_tag_ids)
    this->recipe_tag_ids.insert(recipe_tag_id);
  for (auto food_tag_id: other->food_tag_ids)
    this->food_tag_ids.insert(food_tag_id);
}

/*
 * Returns true if the recipe is compatible with this element
 */
bool DishElement::recipe_compatible(const RecipeData *r) const
{
  if (!hp::in_array(r->dish_type_ids, this->dish_type_id))
    // Wrong dish type id
    return false;
  for (auto recipe_tag_id: this->recipe_tag_ids)
    if (!hp::in_array(r->recipe_tag_ids, recipe_tag_id))
      // One recipe tag is not set
      return false;
  for (auto food_tag_id: this->food_tag_ids)
    if (!hp::in_array(r->food_tag_ids, food_tag_id))
      // One food tag is not set
      return false;
  return true;
}


Dish::~Dish()
{
  for (auto element: this->elements)
    delete element;
}

/*
 * Full copy of Dish AND its DishElements
 */
Dish *
Dish::deepcopy(bool with_elements) const
{
  Dish * res = new Dish(*this);
  res->elements.clear();

  if (!with_elements)
    // Returning an empty dish
    return res;
  for (auto elt: this->elements)
  {
    DishElement *de = new DishElement(*elt);
    res->add_element(de);
  }
  return res;
}

/*
 * Add a dishElement to the dish
 */
void
Dish::add_element(DishElement *e)
{
  this->elements.push_back(e);
  this->elements_per_dish_type_id[e->dish_type_id] = e;
}

/*
 * Add a dishElement to the dish (directly with a dish_type_id)
 */
void
Dish::add_element_from_dt(long dish_type_id)
{
  DishElement *de = new DishElement(dish_type_id);
  this->add_element(de);
}

/*
 * Returns a set of the dish_type ids of this dish elements
 */
std::set<long>
Dish::get_dish_type_ids() const
{
  std::set<long> res;
  for (auto element: this->elements)
    res.insert(element->dish_type_id);
  return res;
}

/*
 * Check that the recipes are compatible with this dish structure
 */
bool Dish::valid_recipes(const DishIndex *di, const RecipeList & recipes) const
{
  if (recipes.size() != this->elements.size())
      return false;  // Mismatch number of recipes

    uint i = 0;
    for (auto element: this->elements)
    {
      if (!(element->recipe_compatible(recipes[i])))
      {
        return false;  // Mismatch dish type
      }
      i++;
    }
    // YAY!
    return true;
}

/*
 * Check that the recipes are compatible with this dish structure OR any of its aggregated variants
 */
bool Dish::valid_recipes_any_variant(const DishIndex *di, const RecipeList & recipes) const
{
  bool res = false;
  std::list<Dish *> variants = di->dishes.at(dish_id)->get_dish_variants(di);

  // Checking if it matches one of the variant (aggregation / non-aggregation)
  for (auto variant: variants)
  {
    if (variant->valid_recipes(di, recipes))
    {
      res = true;
      break;
    }
  }

  // Clearing variants memory
  for (auto variant: variants)
    delete variant;

  return res;
}

void Dish::remove_element(DishElement *de)
{
  this->elements_per_dish_type_id.erase(de->dish_type_id);
  this->elements.remove(de);
  delete de;
}

/*
 * Retrieve a list of dishes with different structures : aggregated / non-aggregated
 */
std::list<Dish *>
Dish::get_dish_variants(const DishIndex *dish_index) const
{
  std::list<Dish *>  res;
  ASSERT(this->elements.size() > 0, "Dish base with no element");

  // If this dish is optional, create an empty version
  if (this->optional)
    res.push_back(this->deepcopy(false));
  // Copy of the original one (aggregated, if so)
  res.push_back(this->deepcopy(true));

  std::set<long> dish_type_ids = this->get_dish_type_ids();
  // We iterate on aggregations to see if one pattern is detected in the dish
  for (auto aggregation: dish_index->dish_type_aggregations)
  {
    if (hp::is_included(dish_type_ids, aggregation.second))
    {
      // We can replace a set of dish_types by an aggregated dish_type
      // Copying the current dish
      Dish * aggregated_dish = this->deepcopy(true);
      // Creating a dish element that will replace the non-aggregated ones
      DishElement *aggregated_dish_element = new DishElement(aggregation.first);
      aggregated_dish->add_element(aggregated_dish_element);
      
      // Merging the non-aggregated dish elements into the aggregated one, and deleting them
      for (auto dt_id: aggregation.second)
      {
        DishElement *old_element = aggregated_dish->elements_per_dish_type_id[dt_id];
        aggregated_dish_element->merge_with(old_element);
        aggregated_dish->remove_element(old_element);
      }
      // Recursive call on aggregated dishes
      res.splice(res.end(), aggregated_dish->get_dish_variants(dish_index));
      delete aggregated_dish;
    }
  }
  return res;
}

Dish * create_dish(long dish_id, long day_id, long meal_id, long meal_type_id, long main_dish_type_id, bool optional, bool external)
{
  return new Dish(dish_id, day_id, meal_id, meal_type_id, main_dish_type_id, optional, external);
}

DishElement * create_dish_element(long dish_type_id)
{
  return new DishElement(dish_type_id);
}

void export_dish()
{
  using namespace boost::python;

  class_<DishElement>("DishElement",        init<long>())
    .def("add_recipe_tag",                  &DishElement::add_recipe_tag)
    .def("add_food_tag",                    &DishElement::add_food_tag);

  class_<Dish>("Dish",                      init<long, long, long, long, long, bool, bool>())
    .def_readonly("id",                     &Dish::dish_id)
    .def("set_initial_ratio",               &Dish::set_initial_ratio)
    .def("add_eater_profile",               &Dish::add_eater_profile)
    .def("add_element",                     &Dish::add_element);

  // Variant to the constructors, that makes the C++ in charge of memory management
  def("create_cpp_dish", &create_dish, return_value_policy<reference_existing_object>());
  def("create_cpp_dish_element", &create_dish_element, return_value_policy<reference_existing_object>());
}