#ifndef FOOD_INDEX_H_
# define FOOD_INDEX_H_

# include <vector>
# include <set>
# include <map>
# include "hippocrate/tools/types.h"

class FoodIndex
{
  public:
    // Constructors
    explicit                  FoodIndex()  {}
    virtual                   ~FoodIndex() {}

    typedef std::map<hp::Id, float>     FoodGrams;
    typedef std::vector<hp::Id>         FoodTags;
    typedef std::map<hp::Id, FoodTags>  TagsMap;
    
    // Public indexes
    FoodGrams                 minimums;
    TagsMap                   tags;
    
    // Adding a food and its minimum quantity (in gram) to the index
    void                      add_food(hp::Id food_id, float minimum, FoodTags & food_tags);
    FoodTags                  get_tags(hp::Id food_id) const { return this->tags.at(food_id); };
    // Return the penalty of a given food according to its quantity
    int                       compute_penalty(hp::Id food_id, long quantity, int cost) const;
    // Check whether a food is in the index or not
    bool                      has_food(hp::Id food_id) { return hp::has_key(this->minimums, food_id); }
};

void export_food_index();

#endif // !FOOD_INDEX_H_