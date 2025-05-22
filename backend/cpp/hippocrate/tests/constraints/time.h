#ifndef HIPPOCRATE_TESTS_CONSTRAINTS_TIME_H_
# define HIPPOCRATE_TESTS_CONSTRAINTS_TIME_H_

# include "hippocrate/tests/algorithm.h"
# include "hippocrate/models/recipe.h"
# include "hippocrate/models/dataindexer.h"

class TimeConstraintFixture : public AlgorithmFixture
{
public:
  
    virtual         ~TimeConstraintFixture() {
      delete this->solution;
    }
  
    virtual void    initRecipeDataIndexer() override {
      RecipeDataIndexer::instance.reset();
      RecipeDataIndexer::instance.add_to_index("prep_minutes");
      RecipeDataIndexer::instance.add_to_index("cook_minutes");
      RecipeDataIndexer::instance.add_to_index("rest_minutes");
    }
  
    virtual void    initRecipe(RecipeData * recipe) override {
        recipe->allocate_data();
        recipe->add_data("prep_minutes", this->default_prep_minutes);
        recipe->add_data("cook_minutes", this->default_cook_minutes);
        recipe->add_data("rest_minutes", this->default_rest_minutes);
    }
    
    void build_solution()
    {
        DarwinAlgorithm         algorithm(this->problem);

        // Initializing DarwinAlgorithm
        DarwinConfig::load("./fixtures/darwin_config_sample.yml");
        this->solution = new Solution(this->problem);
        // Getting a default solution
        *(this->solution) = algorithm.solve();
    }
    
    uint            default_prep_minutes = 20;
    uint            default_cook_minutes = 30;
    uint            default_rest_minutes = 5;
    
    long            meal_id = 0;
    long            cost_per_minute = 10;
    
    Solution        *solution;
};

#endif // HIPPOCRATE_TESTS_CONSTRAINTS_TIME_H_