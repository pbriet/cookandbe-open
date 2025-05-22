#ifndef HIPPOCRATE_MODELS_FILTERS_FILTER_H
# define HIPPOCRATE_MODELS_FILTERS_FILTER_H

# include <boost/noncopyable.hpp>
# include "hippocrate/models/dish.h"
# include "hippocrate/models/recipe.h"

class RecipeFilter : private boost::noncopyable
{
public:
    explicit        RecipeFilter(bool critical = false) : boost::noncopyable(), critical(critical) {}
    virtual         ~RecipeFilter() {}

    virtual bool    accept(const Dish * dish, const RecipeData * recipe) const = 0;

    /*
    Indicates whether the filter is critical or may be removed by hippocrate.
    Today, only diets add critical filter through the ExcludedFoodTag
    */
    bool            critical;
};

class TagRecipeFilter : public RecipeFilter
{
public:
    explicit        TagRecipeFilter(long profile_id, long food_tag_id, bool critical = false);
    virtual         ~TagRecipeFilter();

    virtual bool    accept(const Dish * dish, const RecipeData * recipe) const;

    long            profile_id;
    long            food_tag_id;
};

class ExcludeRecipeFilter : public RecipeFilter
{
public:
    explicit        ExcludeRecipeFilter(long dish_id, long recipe_id);
    virtual         ~ExcludeRecipeFilter();

    virtual bool    accept(const Dish * dish, const RecipeData * recipe) const;

    long            dish_id;
    long            recipe_id;
};

class ExcludeNonHealthyRecipesFilter : public RecipeFilter
{
public:
    explicit        ExcludeNonHealthyRecipesFilter();
    virtual         ~ExcludeNonHealthyRecipesFilter();

    virtual bool    accept(const Dish * dish, const RecipeData * recipe) const;
};

class ExcludeRecipeAllFilter : public RecipeFilter
{
public:
    explicit        ExcludeRecipeAllFilter(long recipe_id);
    virtual         ~ExcludeRecipeAllFilter();

    virtual bool    accept(const Dish * dish, const RecipeData * recipe) const;

    long            recipe_id;
};

class UstensilFilter : public RecipeFilter
{
public:
    explicit        UstensilFilter(long ustensil_id);
    virtual         ~UstensilFilter() {}

    virtual bool    accept(const Dish * dish, const RecipeData * recipe) const;

    long            ustensil_id;
};

/*
 * Exclude recipes with data_key out of some interval
 * Min = -1 or Max = -1 means no limit
 */
class ExcludeDataFilter : public RecipeFilter
{
public:
  explicit      ExcludeDataFilter(const std::string &data_key,
                                  double min_value,
                                  double max_value);

  virtual bool    accept(const Dish * dish, const RecipeData * recipe) const;
  const std::string data_key;
  long              data_id;
  double            min_value;
  double            max_value;
};

class DishTimeFilter : public RecipeFilter
{
public:
    explicit        DishTimeFilter();
    virtual         ~DishTimeFilter() {}

    virtual bool    accept(const Dish * dish, const RecipeData * recipe) const;
    void            add_dish(long dish_id, long max_prep_time, long max_cook_time, long max_rest_time);
    bool            empty() const;

    long            preptime_data_id;
    long            cooktime_data_id;
    long            resttime_data_id;


    // dish_id -> max times
    std::map<long, long>      maximum_prep_times;
    std::map<long, long>      maximum_cook_times;
    std::map<long, long>      maximum_rest_times;
};

void export_recipe_filters();

#endif // HIPPOCRATE_MODELS_FILTERS_FILTER_H
