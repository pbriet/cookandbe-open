
#include <iostream>

#include "hippocrate/models/problem.h"
#include "hippocrate/controls/algorithm/naive/naive.h"
#include "hippocrate/controls/algorithm/darwin/darwin.h"
#include "hippocrate/models/recipeindex.h"
#include "hippocrate/models/filters/filter.h"
#include "hippocrate/tools/container.h"

void
Problem::add_constraint(GenericConstraint * g)
{
  ASSERT(g != nullptr, "Null constraints not allowed");
  g->set_id(this->constraints.size());
  this->constraints.push_back(g);
  
  g->init_rules(this->dish_index);
  
  for (auto rule: g->rules)
  {
    rule->set_id(this->rules_by_id.size());
    this->rules_by_id[rule->id] = rule;
    this->rule_to_parent[rule] = g;
    // Updating a dictionnary of dish set constraints by dish
    for (auto dish_id: rule->dish_ids)
      this->rules_by_dish_id[dish_id].push_back(rule);
  }
}

void Problem::clear_constraints()
{
  this->constraints.clear();
  this->rule_to_parent.clear();
  this->rules_by_dish_id.clear();
}

void
Problem::add_filter(RecipeFilter * f)
{
  ASSERT(f != nullptr, "Null filters not allowed");
  if (f->critical) {
    // Order of critical filters doesn't matter as long as their before "removable" filters
    this->dish_index->recipeFilters.push_front(f);
  } else {
    this->dish_index->recipeFilters.push_back(f);
  }
}


const Rule *
Problem::get_rule(long rule_id) const
{
  ASSERT(hp::has_key(this->rules_by_id, rule_id), "No such rule_id : ", rule_id);
  return this->rules_by_id.at(rule_id);
}

/*
 * Check that constraints ids are unique
 */
void
Problem::assert_validity() const
{
  std::set<long> constraint_ids;
  for (auto constraint: this->constraints)
  {
    ASSERT(constraint->id != -1, "uninitialized constraint id");
    ASSERT(!(hp::in_array(constraint_ids, constraint->id)), "redundant constraint id");
    constraint_ids.insert(constraint->id);
    std::set<long> rule_ids;
    for (auto rule: constraint->rules)
    {
      ASSERT(rule->id != -1, "uninitialized dishset constraint id");
      ASSERT(this->rules_by_id.at(rule->id) == rule, "problem.rules_by_id[id] != rule");
      ASSERT(!(hp::in_array(rule_ids, rule->id)), "redundant dishset constraint id");
      rule_ids.insert(rule->id);
    }
  }
}

void
Problem::init_dishdomains(const RecipeList & ri, bool fillIndexes)
{
  for (auto rdata: ri)
    this->recipe_by_id[rdata->recipe_id] = rdata;
  
  this->dish_index->init_domains(ri, fillIndexes);
  if (this->initial_solution != nullptr)
    this->dish_index->init_bounded_dishes(*(this->initial_solution));
}

void
Problem::set_initial_solution(Solution * solution)
{
    this->initial_solution = solution;
}

Score *
Problem::eval(const Solution *s, bool check_validity)
{
  Score     * sc = new Score(*this);
  
  if (check_validity && !s->isValid()) {
    delete sc;
    RAISE(InvalidSolution, "Invalid solution");
  }
  for (auto constraint: this->constraints) {
    long score = constraint->eval(s, sc);
# if HP_STATS_ENABLED == 1
    this->darwinConstraintTautness[constraint->description()] += score;
# endif
    sc->total += score;
  }
  return sc;
}


/*
 * Given a solution with a total_ratio on a dish, calculates the ratio for the main profile,
 * depending on eaters
 */
void
Problem::calc_main_profile_ratios(Solution &s, long dish_id) const
{
  Dish *d = this->dish_index->dishes[dish_id];
  double total_ratio = s.get_total_recipe_ratio(dish_id);
  
  // Let's calculate the sum of dish eaters ratios
  double total_profile_ratios = 0;
  ASSERT(d->profile_ids.size() > 0, "No profiles in dish");
  ASSERT(this->profile_ratios.size() > 0, "No profile ratios set in problem");
  for (auto prof_id: d->profile_ids)
  {
    if (!hp::has_key(this->profile_ratios, prof_id))
      RAISE(hp::InternalError, sprint("Missing profile ratio"));
    total_profile_ratios += this->profile_ratios.at(prof_id);
  }
  
  // How much does the main profile represents ?
  if (!hp::has_key(this->profile_ratios, this->main_profile_id))
    RAISE(hp::InternalError, sprint("Missing main profile ratio"));
  double main_profile_perc = this->profile_ratios.at(this->main_profile_id) / total_profile_ratios;
  
  // This is the dish ratio for the main profile (total ratio * main profile's part)
  ASSERT(total_ratio * main_profile_perc > 0, "Null main profile ratio");
  s.set_main_profile_recipe_ratio(dish_id, total_ratio * main_profile_perc);
}


/*
 * Tell the problem that this recipe should be a priority at initialization
 */
void 
Problem::add_favorite_recipe(long recipe_id)
{
  // Insert sorted
  auto it = std::lower_bound( this->favorite_recipe_ids.begin(), this->favorite_recipe_ids.end(), recipe_id);
  this->favorite_recipe_ids.insert(it, recipe_id);
}

void py_init_dishdomains(Problem *problem, boost::python::list py_recipe_list, bool fillIndexes=true)
{
  uint nb_recipes = boost::python::len(py_recipe_list);
  RecipeList recipe_list(nb_recipes);
  for (uint j = 0; j < nb_recipes; j++)
    {
      RecipeData *r = boost::python::extract<RecipeData *>(py_recipe_list[j]);
      ASSERT(r, "Failed to extract recipeData in build_solution");
      recipe_list[j] = r;
    }
  problem->init_dishdomains(recipe_list, fillIndexes);
}

void export_problem()
{
  using namespace boost::python;

  class_<Problem>("Problem",            init<DishIndex *, uint>((arg("dish_index"), arg("maximum_solving_time") = 0)))
    .def("add_constraint",              &Problem::add_constraint)
    .def("add_filter",                  &Problem::add_filter)
    .def("init_dishdomains",            &py_init_dishdomains)
    .def("set_main_profile_id",         &Problem::set_main_profile_id)
    .def("set_profile_ratio",           &Problem::set_profile_ratio)
    .def("add_favorite_recipe",         &Problem::add_favorite_recipe)
    
    .def("set_initial_solution",        &Problem::set_initial_solution)
    .def("stick_to_initial_solution",   &Problem::stick_to_initial_solution)
    .def("eval",                        &Problem::eval, return_value_policy<manage_new_object>(),
                                            (arg("solution"), arg("check_validity") = true))
    .def("solve_naive",                 &Problem::solve<NaiveAlgorithm>)
    .def("solve_darwin",                &Problem::solve<DarwinAlgorithm>)
    // Statistics
    .def_readonly("favorite_recipe_ids",                 &Problem::favorite_recipe_ids)
    .def_readonly("darwin_call_stats",                   &Problem::darwinCallStats)
    .def_readonly("darwin_population_variation_score",   &Problem::darwinPopulationVariationScore)
    .def_readonly("darwin_constraint_tautness",          &Problem::darwinConstraintTautness)
    .def_readonly("darwin_best_recipes_per_dishtype",    &Problem::darwinBestRecipesPerDishTypes)
  ;
}
