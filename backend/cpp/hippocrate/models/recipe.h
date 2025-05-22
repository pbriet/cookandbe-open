#ifndef RECIPE_DATA_H_
# define RECIPE_DATA_H_

# include <vector>
# include <list>
# include <map>
# include <string>

#include "hippocrate/models/dataindexer.h"
#include "hippocrate/tools/types.h"

class RecipeData
{
public:
  typedef std::map<long, double>  FoodGrams;
  typedef std::vector<double>     NutrientValues;
  typedef std::map<long, double>  NutrientAvailabilities;
  typedef std::vector<double>     DataArray;
  typedef std::vector<hp::Id>     IdContainer;

  explicit                RecipeData(long recipe_id);

  virtual                 ~RecipeData() {}
  double                  compute_best_ratio(double target_ratio) const;

  inline double           get_data(long data_id, double ratio = 1.0) const { return this->data[data_id] * ratio; }

  // Careful: don't use this one in the algorithm -> might be slow
  double                  get_data_from_key(const std::string &key, double ratio = 1.0) const;

  void                    add_data(const std::string &key, double value);
  void                    allocate_data();

  long                    recipe_id;
  std::wstring            name;
  long                    status;

  // Static array Any id (from RecipeDataIndexer) -> Value (double)
  DataArray               data;

  // Food_id -> grams
  FoodGrams               foods;
  // List of cooking methods ids used by this recipe
  IdContainer             cooking_method_ids;
  // List of Dishtypes for which this recipe can be used
  IdContainer             dish_type_ids;

  // List of recipe tags
  IdContainer             food_tag_ids;
  IdContainer             main_food_tag_ids;  // Food tags with ingredients >= 100g
  IdContainer             suggested_food_tag_ids;  // Relevant food tags for suggestions on recipe page
  IdContainer             recipe_tag_ids;  //  FIXME: not filled yet
  IdContainer             defined_data_ids;

  long                    nb_ingredients = 0;

  bool                    internal;
  bool                    perceived_healthy;

  // Ustensils
  IdContainer             ustensils;
};

typedef std::vector<RecipeData *>       RecipeList;

void export_recipe_data();

#endif