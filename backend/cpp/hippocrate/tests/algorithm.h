
#ifndef TESTS_ALGORITHM_H_
# define TESTS_ALGORITHM_H_

#include "hippocrate/models/solution.h"
#include "hippocrate/models/problem.h"
#include "hippocrate/models/recipeindex.h"
#include "hippocrate/models/dishindex.h"
#include "hippocrate/models/constraints/nutrient.h"
#include "hippocrate/models/recipe.h"
#include "hippocrate/tools/print.h"

class AlgorithmFixture
{
public:
    AlgorithmFixture(uint nbDays = 5, uint nbMealPerDay = 2, uint nbDishPerMeal = 2, uint nbRecipes = 42, uint nbDishTypes = 2)
        : nbDays(nbDays), nbMealPerDay(nbMealPerDay), nbDishPerMeal(nbDishPerMeal), nbRecipes(nbRecipes), nbDishTypes(nbDishTypes)
    {}
    
    virtual void    initialize() {
        this->initRecipeDataIndexer();
        this->initDishIndex();
        this->initRecipeList();   
        this->problem = new Problem(this->dishIndex);
        this->problem->set_main_profile_id(this->main_profile_id);
        this->problem->set_profile_ratio(this->main_profile_id, 1.0);
        this->problem->init_dishdomains(this->recipeList, true);
    }

    virtual         ~AlgorithmFixture() {
        for (auto rdata : this->recipeList)
            delete rdata;
        delete this->problem;
        delete this->dishIndex;
    }
    
    
    
    virtual void    initRecipeList() {
        this->recipeList.resize(this->nbRecipes);
        
        for (uint recipe_id = 0; recipe_id < this->nbRecipes; ++recipe_id)
        {
            RecipeData                          * recipe = new RecipeData(recipe_id);
            RecipeData::FoodGrams               foodGrams;
            RecipeData::NutrientValues          nutrientValues(2);
            RecipeData::NutrientAvailabilities  nutrientAvailabilities;
            
            // Food_id -> grams
            foodGrams[0] = 100 * (1 + recipe_id % this->nbDishTypes);
            foodGrams[1] = 100 * (4 - recipe_id % this->nbDishTypes);
            
            // Nutrient_id -> value
            nutrientValues[0] = 100 * (1 + recipe_id % this->nbDishTypes);
            nutrientValues[1] = 100 * (4 - recipe_id % this->nbDishTypes);
            
            recipe->name = std::to_wstring(recipe_id);
            recipe->foods = foodGrams;
            recipe->cooking_method_ids = { 0 };
            recipe->dish_type_ids = { recipe_id % this->nbDishTypes };
            recipe->data = nutrientValues;
            this->initRecipe(recipe);
            this->recipeList[recipe_id] = recipe;
        }
    }

    virtual void    initDishIndex() {
        this->dishIndex = new DishIndex();
    
        for (uint day = 0; day < this->nbDays; ++day)
            for (uint m = 0; m < this->nbMealPerDay; ++m)
            {
                hp::Id  meal_id      = day * this->nbMealPerDay + m;
                hp::Id  meal_type_id = meal_id % this->nbMealPerDay;
                
                for (uint d = 0; d < this->nbDishPerMeal; ++d)
                {
                    uint dish_id = day * this->nbMealPerDay * this->nbDishPerMeal + m * this->nbDishPerMeal + d;

                    // add_dish_id(long dish_id, long day, long meal_id, long meal_type_id, profile_id, long dish_type_id, double appetence)
                    this->dishIndex->quick_add_dish(dish_id, day, meal_id, meal_type_id, this->main_profile_id, dish_id % this->nbDishTypes);
                }
            }
        this->dishIndex->set_fully_mutable();
    }
    
    virtual uint    nbTotalDishes() {
        return this->nbDays * this->nbMealPerDay * this->nbDishPerMeal;
    }
    
    /*
     * Returns the cost of solution on the current problem
     */
    double get_score_total(const Solution &s) {
      Score * score = this->problem->eval(&s, true);
      long total = score->total;
      delete score;
      return total;
    }

    virtual void    initRecipeDataIndexer() {
      // Here : Add keys in data index if required
    }
    
    virtual void    initRecipe(RecipeData * recipe) {}

protected:
    uint                    nbDays;
    uint                    nbMealPerDay;
    uint                    nbDishPerMeal;
    uint                    nbRecipes;
    uint                    nbDishTypes;
    long                    main_profile_id = 1;
    DishIndex               * dishIndex;
    RecipeList     recipeList;
    Problem                 * problem;
};

#endif // TESTS_ALGORITHM_H_
