
#include <boost/python.hpp>
#include <boost/python/args.hpp>

#include "hippocrate/models/filters/filter.h"
#include "hippocrate/tools/print.h"
#include "hippocrate/tools/container.h"

TagRecipeFilter::TagRecipeFilter(long profile_id, long food_tag_id, bool critical)
    : RecipeFilter(critical), profile_id(profile_id), food_tag_id(food_tag_id)
{}

TagRecipeFilter::~TagRecipeFilter()
{}

bool
TagRecipeFilter::accept(const Dish * dish, const RecipeData * recipe) const
{
    if (!hp::in_array(dish->profile_ids, this->profile_id))
        return true;
    for (auto food_tag_id : recipe->food_tag_ids)
    {
        if (food_tag_id == this->food_tag_id)
            return false;
    }
    return true;
}


ExcludeRecipeFilter::ExcludeRecipeFilter(long dish_id, long recipe_id)
    : RecipeFilter(), dish_id(dish_id), recipe_id(recipe_id)
{}

ExcludeRecipeFilter::~ExcludeRecipeFilter()
{}

bool
ExcludeRecipeFilter::accept(const Dish * dish, const RecipeData * recipe) const
{
  if (dish->dish_id != this->dish_id)
    return true;
  if (recipe->recipe_id == this->recipe_id)
    return false;
  return true;
}

ExcludeNonHealthyRecipesFilter::ExcludeNonHealthyRecipesFilter(): RecipeFilter()
{}

ExcludeNonHealthyRecipesFilter::~ExcludeNonHealthyRecipesFilter()
{}

bool
ExcludeNonHealthyRecipesFilter::accept(const Dish * dish, const RecipeData * recipe) const
{
  return recipe->perceived_healthy;
}

ExcludeRecipeAllFilter::ExcludeRecipeAllFilter(long recipe_id)
    : RecipeFilter(), recipe_id(recipe_id)
{}

ExcludeRecipeAllFilter::~ExcludeRecipeAllFilter()
{}

bool
ExcludeRecipeAllFilter::accept(const Dish * dish, const RecipeData * recipe) const
{
  return recipe->recipe_id != this->recipe_id;
}

UstensilFilter::UstensilFilter(long ustensil_id)
{
  this->ustensil_id = ustensil_id;
}

bool
UstensilFilter::accept(const Dish * dish, const RecipeData * recipe) const
{
  if (hp::in_array(recipe->ustensils, this->ustensil_id))
    return false;
  return true;
}

ExcludeDataFilter::ExcludeDataFilter(const std::string &_data_key,
                                     double _min_value,
                                     double _max_value) : data_key(_data_key),
                                     min_value(_min_value), max_value(_max_value)
{
  this->data_id = RecipeDataIndexer::instance[_data_key];
}

bool
ExcludeDataFilter::accept(const Dish * dish, const RecipeData * recipe) const
{
  double value = recipe->get_data(this->data_id);
  if (this->min_value > 0 && value < this->min_value) {
    return false;
  }
  if (this->max_value > 0 && value > this->max_value) {
    return false;
  }
  return true;
}

DishTimeFilter::DishTimeFilter()
{
  this->preptime_data_id = RecipeDataIndexer::instance["prep_minutes"];
  this->cooktime_data_id = RecipeDataIndexer::instance["cook_minutes"];
  this->resttime_data_id = RecipeDataIndexer::instance["rest_minutes"];
}

void
DishTimeFilter::add_dish(long dish_id, long max_prep_time,
                         long max_rest_time, long max_cook_time)
{
  this->maximum_prep_times[dish_id] = max_prep_time;
  this->maximum_cook_times[dish_id] = max_cook_time;
  this->maximum_rest_times[dish_id] = max_rest_time;
}

bool
DishTimeFilter::accept(const Dish * dish, const RecipeData * recipe) const
{
  long dish_id = dish->dish_id;
  if (!hp::has_key(this->maximum_prep_times, dish_id))
    return true; // No filter on this dish
  if (recipe->get_data(this->preptime_data_id) > this->maximum_prep_times.at(dish_id))
    return false;
  if (recipe->get_data(this->cooktime_data_id) > this->maximum_cook_times.at(dish_id))
    return false;
  if (recipe->get_data(this->resttime_data_id) > this->maximum_rest_times.at(dish_id))
    return false;
  return true;
}

bool
DishTimeFilter::empty() const
{
  return this->maximum_prep_times.size() == 0;
}

void export_recipe_filters()
{
    using namespace boost::python;

    class_<RecipeFilter, boost::noncopyable>("RecipeFilter", no_init)
      .def("accept", &RecipeFilter::accept)
      .def_readonly("critical", &RecipeFilter::critical)
    ;
    class_<TagRecipeFilter, boost::noncopyable, bases<RecipeFilter> >("TagRecipeFilter",
                init<long, long, bool>((arg("profile_id"), arg("food_tag_id"), arg("critical") = false))).
       def_readonly("food_tag_id", &TagRecipeFilter::food_tag_id);
    class_<UstensilFilter, boost::noncopyable, bases<RecipeFilter> >("UstensilFilter", init<long>((arg("ustensil_id"))));
    class_<ExcludeRecipeFilter, boost::noncopyable, bases<RecipeFilter> >("ExcludeRecipeFilter", init<long, long>((arg("dish_id"), arg("recipe_id"))));
    class_<ExcludeNonHealthyRecipesFilter, boost::noncopyable, bases<RecipeFilter> >("ExcludeNonHealthyRecipesFilter", init<>());
    class_<ExcludeRecipeAllFilter, boost::noncopyable, bases<RecipeFilter> >("ExcludeRecipeAllFilter", init<long>((arg("recipe_id"))));
    class_<ExcludeDataFilter, boost::noncopyable, bases<RecipeFilter> >("ExcludeDataFilter", init<const std::string, double, double>((arg("data_key"), arg("min_value"), arg("max_value"))))
       .def_readonly("data_key", &ExcludeDataFilter::data_key)
       .def_readonly("min_value", &ExcludeDataFilter::min_value)
       .def_readonly("max_value", &ExcludeDataFilter::max_value);
    class_<DishTimeFilter, boost::noncopyable, bases<RecipeFilter> >("DishTimeFilter", init<>()).
       def("add_dish", &DishTimeFilter::add_dish).
       def("empty", &DishTimeFilter::empty);
}
