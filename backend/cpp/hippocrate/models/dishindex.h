#ifndef DISH_INDEX_H_
# define DISH_INDEX_H_

# include <vector>
# include <set>
# include <map>
# include "hippocrate/tools/types.h"
# include "hippocrate/models/dish.h"
# include "hippocrate/models/dishdomain.h"

class RecipeFilter;

class DishIndex
{
  public:
    // Constructors
    explicit                    DishIndex() {};
    virtual                     ~DishIndex();

    // Public indexes
    std::map<hp::Id, hp::Ids>   dish_ids_per_day;
    std::map<hp::Id, hp::Ids>   dish_ids_per_meal;
    std::map<hp::Id, hp::Id>    meal_day;
    std::map<hp::Id, hp::Ids>   dish_ids_per_dish_type;
    std::map<hp::Id, hp::Id>    dish_type_per_dish_id;
    std::map<hp::Id, hp::Ids>   meal_ids_per_meal_type_id;
    hp::IdsSet                  external_meal_ids;
    
    // RecipeFilters
    std::list<RecipeFilter *>   recipeFilters;
    // Dishes details
    std::map<long, Dish *>      dishes;

    // Public attributes
    hp::Ids                     all_dish_ids;
    hp::Ids                     mutable_dish_ids;
    
    std::map<long, hp::IdsSet> dish_type_aggregations;  //  Full Dish -> [Main, side]
    std::map<long, hp::IdsSet> dish_type_unions;  //  Drink -> [Cold drink, Hot drink]
    hp::IdsSet                 dish_type_monotony;  // List of monotonous dish_type_ids

    std::map<long, hp::Ids>    bounded_dishes;  //  dish_id -> dish_ids. the other dishes that must change at the same time
    
    void        add_dish(Dish *d);
    void        add_dishtype_aggregation(long master_id, long sub_dish_type_id);
    void        add_dishtype_union(long master_id, long sub_dish_type_id);
    // Shortcut for simple dish structures (one element only)
    void        quick_add_dish(long dish_id, long day_id, long meal_id, long meal_type_id, long profile_id, long dish_type_id);

    // Dish id -> Dish domain options
    std::map<long, DishDomainOptions *>  domains;
    
    // Fills the domains for each dish
    void        init_domains(const RecipeList &recipe_list, bool fill_indexes);
    void        init_bounded_dishes(Solution &initial);
    
    // Shortcut to retrieve a domain for a given dish_id and solution
    DishDomain* get_domain(long dish_id, const Solution *s, bool null_if_not_exists=false) const;
    
    // Returns true if the list of recipe matches the dish structure and its domains
    bool        check_dish_recipes_compatibility(long dish_id, const Solution *s) const;
    bool        check_dish_recipes_compatibility(long dish_id, const RecipeList &recipes) const;
    bool        is_out_of_domain(hp::Id dish_id, const Solution *s) const;
    bool        is_out_of_domain(hp::Id dish_id, const RecipeList &recipes) const;
    
    // Defines which dishes can be mutated / or not (static)
    void        add_mutable_dish(long dish_id);
    void        set_fully_mutable();
    void        set_not_mutable(long dish_id);
    void        add_monotonous_dishype(long dish_type_id);
    hp::Ids     day_dishes(long dish_id) const;
    
private:
    void        init_bounded_dishes_dishtype(Solution &initial, hp::Id dish_type_id);
};

void export_dish_index();

#endif