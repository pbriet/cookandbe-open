#ifndef INDEXES_H_
# define INDEXES_H_

# include <map>
# include <vector>

# include "hippocrate/models/recipe.h"

// Predeclarations
namespace boost { namespace python { class dict; } }



class DetailedRecipeIndex
{
public:
  typedef std::vector<RecipeData *>             RecipeDataVector;
  typedef std::vector<long>                     RecipeDataValuesVector;
  typedef std::vector<int>                      RecipeIds;
  typedef std::map<long, RecipeDataValuesVector > RecipeDataValuesMap;
  
  explicit      DetailedRecipeIndex() {};
  virtual       ~DetailedRecipeIndex(){}

  void          compute_indexes();

  long                               dish_type_id;
  
  // List of all recipes with this dish type
  RecipeDataVector                   all_recipes;
  
  // List all recipes ids
  RecipeIds                          recipe_ids;

  // List of recipes indexed per food contained in recipe
  std::map<long, RecipeDataVector>   per_food;

  // List of recipes indexed per cooking method used in recipe
  std::map<long, RecipeDataVector>   per_cooking_method;

  // The following 2 should be private, but are public for test purposes
  RecipeDataValuesMap                 _data_sorted_values;
  std::map<long, RecipeDataVector>   _data_sorted_recipes;

  void                      add_recipe_data(RecipeData *);
  // Returns a random recipe for this dish type
  RecipeData *              random_recipe();
  RecipeData *              recipe_data_normal(long data_id, double target_value, double variance);

  bool                      empty() const { return this->all_recipes.size() == 0; }
  void                      clear();

  bool                      has_recipe(long recipe_id) const;
  
private:

  void              init_food_idx();
  void              init_cooking_method_idx();
  void              init_data_idx();
  RecipeData        *get_closest_recipe(long nutri_id, double random_nutri_value);
};

class RecipeIndex
{
public:
    explicit                            RecipeIndex() {}
    virtual                             ~RecipeIndex() { this->reset(); }
    
    // Recipe id -> RecipeData
    std::map<long, RecipeData*>         recipes;

    // Initialize the index with a list of recipeData
    void                                add_recipes(RecipeList &recipe_data_vector,
                                                    bool auto_build_index = false);
    void                                add_recipe(RecipeData *r);
    
    void                                build_index();
    
    // Returns true if the index isn't empty
    bool                                ready() const;
    // Empty the index
    void                                reset();
    
    RecipeIndex *                       copy() const;


    // Returns a python dictionnary equivalent of recipes
    boost::python::dict                 get_recipes() const;


    DetailedRecipeIndex                 global_index;
};

void export_dish_type_index();

#endif