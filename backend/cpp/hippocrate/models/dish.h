#ifndef HIPPOCRATE_MODELS_DISH_DETAILS
# define HIPPOCRATE_MODELS_DISH_DETAILS

# include <vector>
# include <set>
# include <list>
# include "hippocrate/models/recipe.h"
# include "hippocrate/models/recipeindex.h"

class DishIndex;

class DishElement
{
public:
  DishElement(long _dish_type_id) :
    dish_type_id(_dish_type_id) {};

  void add_recipe_tag(long id) { this->recipe_tag_ids.insert(id); }
  void add_food_tag(long id) { this->food_tag_ids.insert(id); }

  void merge_with(const DishElement *other);

  // Returns true if the recipe is compatible with this element
  bool recipe_compatible(const RecipeData *r) const;
  
  // Filters on RecipeTag and FoodTag
  std::set<long>       recipe_tag_ids;
  std::set<long>       food_tag_ids;
  
  long dish_type_id;
};

class Dish
{
public:
  explicit  Dish() = delete;
  explicit  Dish(const Dish & dish) = default;
  explicit  Dish(long _dish_id, long _day_id, long _meal_id, long _meal_type_id, long _main_dish_type_id, bool _optional, bool _external) :
    dish_id(_dish_id), day_id(_day_id), meal_id(_meal_id), meal_type_id(_meal_type_id),
    main_dish_type_id(_main_dish_type_id), optional(_optional), external(_external)
  {}
  virtual   ~Dish();

  // Full copy of Dish AND its DishElements
  Dish *                deepcopy(bool with_elements=true) const;
  
  void                  add_element(DishElement *e);
  void                  add_element_from_dt(long dish_type_id);
  void                  remove_element(DishElement *de);
  std::set<long>        get_dish_type_ids() const;

  // Check that the recipes are compatible with this dish structure
  bool                  valid_recipes(const DishIndex *di, const RecipeList & recipes) const;

  // Check that the recipes are compatible with this dish structure OR any of its aggregated variant
  bool                  valid_recipes_any_variant(const DishIndex *di, const RecipeList & recipes) const;

  // Retrieve a list of dishes with different structures : aggregated / non-aggregated
  std::list<Dish *>     get_dish_variants(const DishIndex *dish_index) const;
  
  // Initialize the global ratio (sum of eaters) of this dish
  void                  set_initial_ratio(double value) { this->initial_global_ratio = value; };
  void                  add_eater_profile(long id) { this->profile_ids.insert(id); }
  
  // what's in the dish : elements with dish_type and tags
  // Dish type id -> Dish element
  std::list<DishElement *>          elements;
  std::map<long, DishElement *>     elements_per_dish_type_id;
  long                              dish_id;
  long                              day_id;
  long                              meal_id;
  long                              meal_type_id;
  long                              main_dish_type_id;
  bool                              optional; // This dish can be skipped (no recipe)
  bool                              external;
  std::set<long>                    profile_ids; // eaters
  
  double                            initial_global_ratio = -1; // This is the ratio "reference", which is initialized
};


void export_dish();

#endif