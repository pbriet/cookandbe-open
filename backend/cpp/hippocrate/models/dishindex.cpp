
#include <boost/python.hpp>
#include <algorithm>

#include "hippocrate/tools/container.h"
#include "hippocrate/models/dishindex.h"
#include "hippocrate/models/solution.h"
#include "hippocrate/models/filters/filter.h"

DishIndex::~DishIndex()
{
  for (auto dish_pair: this->dishes)
    delete dish_pair.second;
  for (auto domain_options_pair: this->domains)
    delete domain_options_pair.second;
  // recipeFilters are managed by Python
}

/*
 * Add a dish in the index  (test helper)
 */
void
DishIndex::quick_add_dish(long dish_id, long day_id, long meal_id, long meal_type_id, long profile_id, long dish_type_id)
{
  Dish *d = new Dish(dish_id, day_id, meal_id, meal_type_id, dish_type_id, false, false);
  DishElement *de = new DishElement(dish_type_id);
  d->add_element(de);
  d->add_eater_profile(profile_id);
  d->set_initial_ratio(1.0);
  this->add_dish(d);
}

/*
 * Add a dish in the index
 */
void
DishIndex::add_dish(Dish *d)
{
  this->dishes[d->dish_id] = d;
  hp::default_get(this->dish_ids_per_day, d->day_id).push_back(d->dish_id);
  hp::default_get(this->dish_ids_per_meal, d->meal_id).push_back(d->dish_id);
  this->meal_day[d->meal_id] = d->day_id;

  for (auto element: d->elements)
    hp::default_get(this->dish_ids_per_dish_type, element->dish_type_id).push_back(d->dish_id);

  this->dish_type_per_dish_id[d->dish_id] = d->main_dish_type_id;
  
  // Insert sorted in all_dish_ids
  hp::Ids::iterator insert_it = std::lower_bound(this->all_dish_ids.begin(),
                                                 this->all_dish_ids.end(), d->dish_id);
  this->all_dish_ids.insert(insert_it, d->dish_id);
  
  // Update meals
  if (!hp::has_key(this->meal_ids_per_meal_type_id, d->meal_type_id) ||
      this->meal_ids_per_meal_type_id[d->meal_type_id].back() != d->meal_id) {
    ASSERT(!hp::in_array(hp::default_get(this->meal_ids_per_meal_type_id, d->meal_type_id), d->meal_id), "meal id", d->meal_id, "already in vector");
    hp::default_get(this->meal_ids_per_meal_type_id, d->meal_type_id).push_back(d->meal_id);
  }
  if (d->external) {
    this->external_meal_ids.insert(d->meal_id);
  }
}

/*
 * Add a dish aggregation in the index
 */
void
DishIndex::add_dishtype_aggregation(long master_id, long sub_dish_type_id)
{
  hp::default_get(this->dish_type_aggregations, master_id).insert(sub_dish_type_id);
}

/*
 * Add a dish union in the index
 */
void
DishIndex::add_dishtype_union(long master_id, long sub_dish_type_id)
{
  hp::default_get(this->dish_type_unions, master_id).insert(sub_dish_type_id);
}

/*
 * Fills the domains for each dish
 */
void
DishIndex::init_domains(const RecipeList &recipe_list, bool fill_indexes)
{
  for (auto dish_id: this->mutable_dish_ids)
  {
    this->domains[dish_id] = new DishDomainOptions(dish_id);
    
    Dish *d = this->dishes[dish_id];
    // For a given dish, we retrieve all its possible variants  (aggregated, non-aggregated)
    // memory: dish_variant is given to DishDomain, which will delete it
    std::list<Dish *> dish_variants = d->get_dish_variants(this);

    for (auto dish_variant: dish_variants)
    {
      DishDomain *dish_domain = new DishDomain(dish_variant);
      if (fill_indexes) {
        dish_domain->init_from_dish(recipe_list, dish_variant, this->recipeFilters);
      }
      
      this->domains[dish_id]->options.push_back(dish_domain);
    }
  }
}


/*
 * Based on monotonous dish_types, defines what dishes are bound together.
 * It means that when one of them changes, the other must be modified the same way
 */
void
DishIndex::init_bounded_dishes(Solution &initial)
{
  for (auto dish_type_id: this->dish_type_monotony)
    this->init_bounded_dishes_dishtype(initial, dish_type_id);
}

void
DishIndex::init_bounded_dishes_dishtype(Solution &solution, hp::Id dish_type_id)
{
  hp::Ids &monotonous_dishids = this->dish_ids_per_dish_type[dish_type_id];
  hp::Ids mutables;
  mutables.reserve(monotonous_dishids.size());
  
  // In this dish_type, what are the mutables dishes
  for (auto dish_id: monotonous_dishids)
    if (hp::in_array(this->mutable_dish_ids, dish_id))
      mutables.push_back(dish_id);

  // The following block has been disabled after transforming NotNow from filter to constraint
  // if (mutables.size() != monotonous_dishids.size())
  // {
  //   // Some dishes aren't mutable  (forced / fixed)
  //   bool all_compatible_with_domain = true;
  //   for (auto dish_id: mutables)
  //     if (!this->check_dish_recipes_compatibility(dish_id, &solution))
  //     {
  //       // One of the dish at least is not compatible with its domain
  //       all_compatible_with_domain = false;
  //       break;
  //     }
  //   if (all_compatible_with_domain)
  //   {
  //     // One dish at least is forced, and every dish is currently compatible with its domain
  //     // in the initial solution
  //     // Let's remove the dishes from mutables
  //     for (auto mutable_dish_id: mutables)
  //       this->set_not_mutable(mutable_dish_id);
  //     return;
  //   }
  // }
  
  // Either all the dishes are mutable, or some aren't but there are incompatibilities with domains
  // => Bind mutables together. When one will be changed, the other will do the same
  for (auto dish_id1: mutables)
  {
    this->bounded_dishes[dish_id1].reserve(mutables.size() - 1);
    for (auto dish_id2: mutables)
      if (dish_id1 != dish_id2)
        this->bounded_dishes[dish_id1].push_back(dish_id2);
  }
}

/*
 * Given a dish_id and a solution
 * Returns true if current solution on this dish is out of its domain  (theorically non-autorized)
 */
bool
DishIndex::is_out_of_domain(hp::Id dish_id, const Solution *s) const
{
  const DishDomainOptions *domo = this->domains.at(dish_id);
  // Are the dish recipes in the domain ?
  return !(domo->check_recipes_in_domain(s));
}

bool
DishIndex::is_out_of_domain(hp::Id dish_id, const RecipeList &recipes) const
{
  const DishDomainOptions *domo = this->domains.at(dish_id);
  // Are the dish recipes in the domain ?
  return !(domo->check_recipes_in_domain(this, recipes));
}

/*
 * Returns true if the list of recipe matches the dish structure and its domains
 * WARNING : works only on dish_ids with domains, i.e. mutable dish_ids
 */
bool
DishIndex::check_dish_recipes_compatibility(long dish_id, const RecipeList &recipes) const
{
  if (!(this->dishes.at(dish_id)->valid_recipes_any_variant(this, recipes)))
    // Something is wrong with this dish
    return false;
  return !(this->is_out_of_domain(dish_id, recipes));
}

bool
DishIndex::check_dish_recipes_compatibility(long dish_id, const Solution *s) const
{
  return this->check_dish_recipes_compatibility(dish_id, s->get_recipe_list(dish_id));
}


/*
 * For a given solution and dish, returns the DishDomain
 */
DishDomain*
DishIndex::get_domain(long dish_id, const Solution *s, bool null_if_not_exists) const
{
  if (!null_if_not_exists) {
    ASSERT(hp::has_key(this->domains, dish_id), "No domain for dish", dish_id);
  }
  else if (!hp::has_key(this->domains, dish_id))
    return 0;
  return this->domains.at(dish_id)->domain_from_solution(s);
}

/*
 * Only some dishes are mutable
 */
void   DishIndex::add_mutable_dish(long dish_id)
{
    this->mutable_dish_ids.push_back(dish_id);
}

/*
 * All dishes are mutable
 */
void   DishIndex::set_fully_mutable()
{
    this->mutable_dish_ids = this->all_dish_ids;
}


void
DishIndex::set_not_mutable(long dish_id)
{
    hp::remove_from(this->mutable_dish_ids, dish_id, false);
}

void
DishIndex::add_monotonous_dishype(long dish_type_id)
{
  this->dish_type_monotony.insert(dish_type_id);
}


hp::Ids
DishIndex::day_dishes(long dish_id) const
{
  if (hp::has_key(this->dish_ids_per_day, dish_id))
    return this->dish_ids_per_day.at(dish_id);
  hp::Ids empty;
  return empty;
}

void export_dish_index()
{
  using namespace boost::python;

  class_<DishIndex>("DishIndex",        init<>())
    .def_readonly("mutable_dish_ids",   &DishIndex::mutable_dish_ids)
    .def_readonly("all_dish_ids",       &DishIndex::all_dish_ids)
    .def("day_dishes",                  &DishIndex::day_dishes)
    .def("add_dish",                    &DishIndex::add_dish)
    .def("set_fully_mutable",           &DishIndex::set_fully_mutable)
    .def("set_not_mutable",             &DishIndex::set_not_mutable)
    .def("add_monotonous_dishype",      &DishIndex::add_monotonous_dishype)
    .def("add_mutable_dish",            &DishIndex::add_mutable_dish)
    .def("add_dishtype_aggregation",    &DishIndex::add_dishtype_aggregation)
    .def("add_dishtype_union",          &DishIndex::add_dishtype_union);
}