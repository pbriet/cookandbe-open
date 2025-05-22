
#include <boost/python.hpp>
#include <boost/python/dict.hpp>
#include <algorithm>

#include "hippocrate/models/solution.h"
#include "hippocrate/models/problem.h"
#include "hippocrate/wrapstd.h"
#include "hippocrate/tools/random.h"
#include "hippocrate/tools/container.h"
#include "hippocrate/models/recipeindex.h"

Solution::Solution(Problem * p) :
  problem(p)
{
    // Initialize dish ratios with the default ones
      this->init_dish_ratios();
}

void
Solution::clear()
{
  this->_dish_id_to_recipes.clear();
  this->_dish_ratios.clear();
  this->constraint_buffer.clear();
}

bool
Solution::isValid(bool check_domains) const
{
  DishIndex * di = this->problem->dish_index;
  if (this->_dish_id_to_recipes.size() < di->all_dish_ids.size())
    return false;  //  Some dishes are not in the solution dictionnary
  for (auto dish_id_to_recipes: this->_dish_id_to_recipes)
  {
    long dish_id = dish_id_to_recipes.first;
    ASSERT(hp::has_key(di->dishes, dish_id), "Invalid dish_id in solution");
    if (!(di->dishes.at(dish_id)->valid_recipes_any_variant(di, dish_id_to_recipes.second)))
      // Something is wrong with this dish
      return false;
  }
  if (check_domains)
  {
# ifdef DEBUG
    // Check that all dish recipes are within the domains
    for (auto dish_id: di->mutable_dish_ids)
    {
      ASSERT(hp::has_key(this->problem->dish_index->domains, dish_id), "No domain for a dish id !");
      ASSERT( this->problem->dish_index->domains.at(dish_id)->check_recipes_in_domain(this), "Recipe not in domain!");
    }
#endif
  }
  return true;
}

void
Solution::randomize()
{
  for (auto dish_id: this->problem->dish_index->mutable_dish_ids)
    this->randomize_dish(dish_id);
}

/*
 * Randomize dishes for which the recipes that are set do not belong to the domain
 * (the domains have changed since the solution was generated)
 */
void
Solution::randomize_out_of_domain()
{
  DishIndex * dish_index = this->problem->dish_index;
  for (auto dish_id: this->problem->dish_index->mutable_dish_ids)
  {
    if (dish_index->is_out_of_domain(dish_id, this))
      this->randomize_dish(dish_id);
  }
}

/*
 * Initialize the dish ratios from Dish::initial_ratios
 */
void Solution::init_dish_ratios()
{
    for (auto dish_id: this->problem->dish_index->all_dish_ids)
    {
        const Dish        * dish   = this->problem->dish_index->dishes.at(dish_id);
        ASSERT(dish->initial_global_ratio > 0, "non-initialized global ratio on dish", dish_id);
        this->_dish_ratios[dish_id] = dish->initial_global_ratio;
        this->problem->calc_main_profile_ratios(*this, dish_id);
    }
}

void
Solution::set_recipe(long dish_id, long position, RecipeData * recipe, bool call_handlers, bool monotony_rec)
{
  if (call_handlers)
    this->call_rm_recipes_handlers(dish_id);
  if (position == 0)
  {
    ASSERT(hp::has_key(this->_dish_ratios, dish_id), "Set recipe with no ratio currently set");
    double current_ratio = this->_dish_ratios.at(dish_id);
    ASSERT(current_ratio >= 0.1, "Very low ratio");
    // Storing ratio. compute_best_ratio modifies it if some ingredients have discrete values (TODO)
    this->_dish_ratios[dish_id] = recipe->compute_best_ratio(current_ratio);
  }
  this->_dish_id_to_recipes[dish_id][position] = recipe;

  this->problem->calc_main_profile_ratios(*this, dish_id);

  if (call_handlers)
    this->call_add_recipes_handlers(dish_id);
  if (position == 0 && monotony_rec) // Ensuring position is 0 for security
    this->call_monotony_recursion(dish_id);
}


void
Solution::set_recipe_list(long dish_id, const RecipeList & recipes, double ratio, bool monotony_rec)
{
  if (hp::has_key(this->_dish_id_to_recipes, dish_id))
    this->call_rm_recipes_handlers(dish_id);
  this->_dish_id_to_recipes[dish_id] = recipes;
  if (ratio > 0)
    this->_dish_ratios[dish_id] = ratio;
  if (!recipes.empty())
  {
    // Set the correct ratio
    this->set_recipe(dish_id, 0, recipes[0], false, false);
    if (monotony_rec)
      this->call_monotony_recursion(dish_id);
  }
  else
    this->problem->calc_main_profile_ratios(*this, dish_id);

  this->call_add_recipes_handlers(dish_id);
}

/*
 * Check if the dish has a monotonous dish_type.
 * If so, modify all the dishes of the same dish_type, by
 * setting the same recipe to all.
 */
void
Solution::call_monotony_recursion(long dish_id)
{
  const RecipeList &recipes = this->get_recipe_list(dish_id);
  const DishIndex * dish_index = this->problem->dish_index;
  if (hp::has_key(dish_index->bounded_dishes, dish_id))
  {
    // This is a monotonous dish_type. All the other dishes of the same dish_type
    // should be set with the same recipe
    for (auto similar_dish_id: dish_index->bounded_dishes.at(dish_id))
    {
      const RecipeList &existing_recipes = this->get_recipe_list(similar_dish_id);
      if (!existing_recipes.empty() && existing_recipes != recipes &&
          !dish_index->is_out_of_domain(similar_dish_id, recipes))
        this->set_recipe_list(similar_dish_id, recipes, -1, false);
    }
  }
}

void Solution::change_dish_ratio(long dish_id, double new_ratio)
{
  // Resetting the buffered constraint data
  this->call_rm_recipes_handlers(dish_id);
  this->_dish_ratios[dish_id] = new_ratio;
  this->problem->calc_main_profile_ratios(*this, dish_id);
  this->call_add_recipes_handlers(dish_id);
}

const RecipeData *
Solution::get_recipe(long dish_id, long position) const
{
  ASSERT(hp::has_key(this->_dish_id_to_recipes, dish_id), "Can't find dish", dish_id, "in solution (", this->_dish_id_to_recipes, ")");
  return this->_dish_id_to_recipes.at(dish_id)[position];
}

const RecipeList &
Solution::get_recipe_list(long dish_id) const
{
  ASSERT(hp::has_key(this->_dish_id_to_recipes, dish_id), "Can't find dish", dish_id, "in solution (", this->_dish_id_to_recipes, ")");
  return this->_dish_id_to_recipes.at(dish_id);
}

double
Solution::get_total_recipe_ratio(long dish_id) const
{

  if (!hp::has_key(this->_dish_ratios, dish_id))
    RAISE(hp::InternalError, sprint("No total ratio set for dish"));
  return this->_dish_ratios.at(dish_id);
}

double
Solution::get_main_profile_recipe_ratio(long dish_id) const
{
  if (!hp::has_key(this->_dish_main_profile_ratios, dish_id))
    RAISE(hp::InternalError, sprint("No main profile ratio set for dish"));
  return this->_dish_main_profile_ratios.at(dish_id);
}

/*
 * This dish type is an aggregated dish type
 * * If the current recipe is an aggregated one
 *   - replace it by another one
 *   - or replace it by a list of splitted recipes
 * * If the current recipe list is a split of the aggregated one
 *   - replace one of the recipes
 *   - replace it by a an aggregated one
 */
void
Solution::randomize_dish(long dish_id, const std::vector<hp::Id> *prior_recipe_ids)
{
  DishIndex * dish_index = this->problem->dish_index;

  // Select the domain
  DishDomainOptions* domain_options = dish_index->domains.at(dish_id);
  DishDomain * domain               = domain_options->random_domain();

  // Pick recipes in the domain
  RecipeList  recipe_list;
  for (auto index: domain->indexes)
  {
    if (prior_recipe_ids && prior_recipe_ids->size() > 0) {
      // Pick a random value in the intersection of index recipes and prior recipes
      std::vector<hp::Id> intersect_values(prior_recipe_ids->size());
      auto iterator = std::set_intersection(prior_recipe_ids->begin(), prior_recipe_ids->end(),
                                            index->recipe_ids.begin(), index->recipe_ids.end(),
                                            intersect_values.begin());
      intersect_values.resize(iterator - intersect_values.begin());
      if (intersect_values.size() > 0)
      {
        hp::Id recipe_id = RandomGenerator::getInstance().pick(intersect_values);
        // There is a prior_recipe that can be assigned. Do it and remove it from the list.
        ASSERT(hp::has_key(this->problem->recipe_by_id, recipe_id), "No such recipe id in problem recipe_by_id");
        recipe_list.push_back(this->problem->recipe_by_id[recipe_id]);
        continue;
      }
    }
    recipe_list.push_back(index->random_recipe());
  }
  this->set_recipe_list(dish_id, recipe_list);
}

/*
* Randomize one recipe in a given dish
*/
void Solution::randomize_dishrecipe(long dish_id, long recipe_no)
{
  DishIndex * dish_index = this->problem->dish_index;

  // Retrieve the domain
  DishDomain *domain = dish_index->get_domain(dish_id, this);

  ASSERT(recipe_no < ((long)domain->indexes.size()), "Domain index is too small");
  // Pick a random recipe
  RecipeData *recipe = domain->indexes[recipe_no]->random_recipe();

  this->set_recipe(dish_id, recipe_no, recipe, true, true);
}


/*
 * For each dish, try to take a recipe from favorites. If there is none available, randomize.
 */
void
Solution::init_from_favorites()
{
  // Copying the vector
  std::vector<hp::Id> favorite_ids = this->problem->favorite_recipe_ids;

  for (auto dish_id: this->problem->dish_index->mutable_dish_ids)
    this->randomize_dish(dish_id, &favorite_ids);
}

/*
 *Calls rm_recipes handlers on the constraints affected by a change in a dish_id
 */
void
Solution::call_rm_recipes_handlers(long dish_id)
{
  for (auto rule: this->problem->rules_by_dish_id[dish_id])
    rule->on_solution_rm_recipes(this, dish_id);
}

/*
 *Calls add_recipes handlers on the constraints affected by a change in a dish_id
 */
void
Solution::call_add_recipes_handlers(long dish_id)
{
  for (auto rule: this->problem->rules_by_dish_id[dish_id])
    rule->on_solution_new_recipes(this, dish_id);
}

/*
 * Function that MUST be called if the solution is built with build_solution(call_handlers=False)
 * and ONLY in that case.
 * It will initialize the optimization buffers (one buffer per contraint)
 */
void
Solution::init_constraint_buffers()
{
  for (auto it: this->problem->dish_index->all_dish_ids)
    this->call_add_recipes_handlers(it);
}

/*
 * Handy method to create a solution Python-side, from a problem
 * and a dictionnary {recipe_id : [RecipeData]}
 *
 * Warning : if you add the constraints AFTER building a solution, please call init_constraint_buffers() afterwise
 */
Solution *
build_solution(Problem *p, boost::python::dict dishid_to_recipes, boost::python::dict dish_id_to_ratio)
{
  Solution * s = new Solution(p);
  boost::python::list   keys = dishid_to_recipes.keys();

  for (uint i = 0; i < boost::python::len(keys); i++)
  {
    long dish_id                       = boost::python::extract<long>(keys[i]);
    boost::python::list py_recipe_list = boost::python::extract<boost::python::list>(dishid_to_recipes[keys[i]]);

    RecipeList  recipe_list;
    for (uint j = 0; j < boost::python::len(py_recipe_list); j++)
    {
      RecipeData *r = boost::python::extract<RecipeData *>(py_recipe_list[j]);
      ASSERT(r, "Failed to extract recipeData in build_solution");
      recipe_list.push_back(r);
    }
    s->set_dish_ratio(dish_id, boost::python::extract<double>(dish_id_to_ratio[keys[i]]));
    s->set_recipe_list(dish_id, recipe_list, -1, false); // No monotony recursion
  }
  return s;
}

/*
 * Returns to python a dictionnary
 *  dish_id  -->  list of DishRecipes
 */
static boost::python::dict
py_get_dish_id_to_dishrecipes(const Solution * solution)
{
  boost::python::dict res;
  for (long dish_id: solution->problem->dish_index->all_dish_ids)
  {
    boost::python::list recipe_list;
    long i_recipe = 0;
    DishDomain *domain = solution->problem->dish_index->get_domain(dish_id, solution, true);
    bool fully_filtered = false;
    if (domain)
      fully_filtered = domain->fully_filtered;
    for (auto recipe: solution->get_recipe_list(dish_id))
    {
      DishRecipe dr(dish_id, recipe, i_recipe++,
                    solution->get_total_recipe_ratio(dish_id), fully_filtered);
      recipe_list.append(dr);
    }
    res[dish_id] = recipe_list;
  }
  return res;
}

static boost::python::dict
py_get_dish_id_to_recipes(const Solution * solution) {
  boost::python::dict res;
  for (auto r_pair: solution->get_all_recipes())
  {
    boost::python::list recipe_list;
    for (auto recipe: r_pair.second)
      recipe_list.append(recipe);
    res[r_pair.first] = recipe_list;
  }
  return res;
}

void
export_solution()
{
  using namespace boost::python;

  class_<Solution>("Solution", no_init)
    .def("get_main_profile_recipe_ratio",   &Solution::get_main_profile_recipe_ratio)
    .def("get_total_recipe_ratio",          &Solution::get_total_recipe_ratio)
    .def("get_dish_recipes",                &py_get_dish_id_to_dishrecipes)
    .def("get_recipes",                     &py_get_dish_id_to_recipes)
    .def("isValid",                         &Solution::isValid)
    .def("init_constraint_buffers",         &Solution::init_constraint_buffers);

  def("build_solution", &build_solution, return_value_policy<manage_new_object>());
}