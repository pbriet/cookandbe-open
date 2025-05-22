#include <iostream>
#include <cassert>
#include <cmath>
#include <map>
#include <vector>

#include "hippocrate/controls/algorithm/darwin/darwin.h"
#include "hippocrate/controls/algorithm/darwin/config.h"
#include "hippocrate/controls/algorithm/darwin/logger.h"
#include "hippocrate/controls/algorithm/darwin/selection.h"
#include "hippocrate/controls/algorithm/darwin/exceptions.h"
#include "hippocrate/tools/random.h"
#include "hippocrate/tools/container.h"
#include "hippocrate/tools/exception.h"
#include "hippocrate/models/problem.h"

DarwinAlgorithm::DarwinAlgorithm(Problem *p) :
  Algorithm(p),
  random_crossover(new RandomMateCrossover(this)),
  oriented_crossover(new ProportionalConstraintBetterMateCrossover(this)),
  random_mutation(new RandomMutation(this)),
  oriented_mutation(new ScoreOrientedMutation(this))
{
  ASSERT(this->random_crossover != nullptr, "Darwin: no random crossover operator");
  ASSERT(this->oriented_crossover != nullptr, "Darwin: no oriented crossover operator");
  ASSERT(this->random_mutation != nullptr, "Darwin: no random mutation operator");
  ASSERT(this->oriented_mutation != nullptr, "Darwin: no oriented mutation operator");
}

/*
 * Freeing memory
 */
DarwinAlgorithm::~DarwinAlgorithm()
{
  for (auto solution: this->population)
    delete solution;
  for (auto solution_to_score: this->scores)
    delete solution_to_score.second;
  delete this->random_crossover;
  delete this->oriented_crossover;
  delete this->random_mutation;
  delete this->oriented_mutation;
}

void
DarwinAlgorithm::check_validity_before_start() const
{
  ASSERT(this->problem->dish_index->dishes.size(), "empty planning");
  ASSERT(this->problem->dish_index->domains.size(), "domains not initialized");
  this->problem->assert_validity();
}

/*
 * Main function for Darwin algorithm.
 * Using genetic algorithms.
 */
Solution
DarwinAlgorithm::solve()
{
  DARWIN_START_PROFILING();
  #ifndef NDEBUG
    this->check_validity_before_start();
  #endif
  // Configuration must has been loaded before using the darwin algorithm
  if (!DarwinConfig::is_loaded(true))
    RAISE(DarwinConfigMustBeReadyException);
  this->init_constraints();
  this->init_population();
  this->evaluate();
  this->start_solving_time();
  
  while (this->should_continue())
  {
    this->cross();
    this->mutate();
    this->add_children();
    this->evaluate();
    this->select();
  }
  DARWIN_END_PROFILING();
  Solution *best_solution = this->population.front();
#if HP_STATS_ENABLED == 1
  this->compute_population_variation();
#endif
  // Returning the best solution (first in list)
  return *best_solution;
}

/*
 * Add children into population, and clear children list
 */
void
DarwinAlgorithm::add_children()
{
  HP_STAT_AUTOSAVE(this->problem->darwinCallStats, "add_children");
  for (auto solution: this->children)
    this->population.push_back(solution);
  this->children.clear();
}

/*
 * Returns true if the algorithm should continue to
 * create a new generation
 */
bool
DarwinAlgorithm::should_continue()
{
  HP_STAT_AUTOSAVE(this->problem->darwinCallStats, "should_continue");
  DARWIN_LOG("========= GENERATION ", this->generation_no, "===============");
  Solution *best_solution       = this->population.front();
  long      best_solution_score = this->scores[best_solution]->total;

  DARWIN_LOG("----> Best solution (", best_solution, ") = ", best_solution_score);
  DARWIN_PROFILE(best_solution_score);

  // Check if this is a lost generation or not
  if (best_solution_score == this->last_best_score)
    this->nb_lost_generations++;
  else
  {
    this->nb_lost_generations = 0;
    this->last_best_score = best_solution_score;
  }

  // Update the cross/mutation rates
  long nb_generations = DarwinConfig::get<long>("nb_generations");
  this->generation_no++;
  double generation_progress = ((double) this->generation_no) / nb_generations;
  // Updating oriented crossovers/mutations rate
  this->oriented_cross_rate = DarwinConfig::get<double>("oriented_crossover_rate_end") * generation_progress +\
                              DarwinConfig::get<double>("oriented_crossover_rate_start") * (1 - generation_progress);
  this->oriented_mutation_rate = DarwinConfig::get<double>("oriented_mutation_rate_end") * generation_progress +\
                                 DarwinConfig::get<double>("oriented_mutation_rate_start") * (1 - generation_progress);

  // Score == 0 or too many lost generations ? The end...
  if (best_solution_score == 0 or
      this->nb_lost_generations > DarwinConfig::get<long>("max_lost_generations") or
      this->solving_time_exceeded())
    return false;
  
  // Continue while generation no is lower than number of generations
  return this->generation_no < nb_generations;
}

/*
 * Cross solutions to create new ones
 */
void
DarwinAlgorithm::cross()
{
  long nb_crossovers = this->population.size() * DarwinConfig::get<double>("crossover_rate");
  HP_STAT_AUTOSAVE(this->problem->darwinCallStats, "cross");

  for (int i = 0; i < nb_crossovers; i++)
  {
    Solution * individual = RandomGenerator::pick(this->population);

    if (this->scores[individual]->total > 0 && RandomGenerator::in_percentage(this->oriented_cross_rate))
      this->oriented_crossover->cross(individual);
    else
      this->random_crossover->cross(individual);
  }
}


/*
 * Apply some mutations on solutions
 */
void
DarwinAlgorithm::mutate()
{
  HP_STAT_AUTOSAVE(this->problem->darwinCallStats, "mutate");
  long nb_mutations = this->population.size() * DarwinConfig::get<double>("mutation_rate");
  
  for (int i = 0; i < nb_mutations; i++)
  {
    Solution * individual = RandomGenerator::pick(this->population);

    if (this->scores[individual]->total > 0 && RandomGenerator::in_percentage(this->oriented_mutation_rate))
      this->oriented_mutation->mutate(individual);
    else
      this->random_mutation->mutate(individual);
  }
}

/*
 * Evaluate solutions and sort them
 */
void
DarwinAlgorithm::evaluate()
{
  HP_STAT_AUTOSAVE(this->problem->darwinCallStats, "evaluate");
  hp::darwin::PopulationScores  new_scores;

  std::vector<long>     costs_vector(this->population.size());
  uint                  i_pop = 0;
  
  // For each solution, calculates cost
  for (auto solution: this->population)
  {
    if (hp::has_key(this->scores, solution))
    {
      // A solution that was already there in the previous generation
      new_scores[solution] = this->scores[solution];
      this->scores.erase(solution); // Removing it -> the score won't be freed
    }
    else
    {
      // New solution
      Score *solution_score = this->problem->eval(solution, false);
      new_scores[solution] = solution_score;
    }
    costs_vector[i_pop++] = new_scores[solution]->total;
  }
  // Sorting solutions by costs
  hp::sort_from_first_vector(costs_vector, this->population);

  for (auto solution_score: this->scores)
    delete solution_score.second;
  this->scores = new_scores;
}

/*
 * Keep only the best solutions
 */
void
DarwinAlgorithm::select()
{
  HP_STAT_AUTOSAVE(this->problem->darwinCallStats, "select");
  std::string selection_method = DarwinConfig::get<std::string>("selection");
  if (selection_method == "elitism")
    Elitism(this->population, this->scores).select();
  else if (selection_method == "rankproportionate")
    RankProportionateSelection(this->population, this->scores).select();
  else
    RAISE(DarwinCriticalException, "Unknown or undefined selection method");
}


/*
 * Detects and selects the constraints that can be mutated
 * <> the constraints set on dishes that can be mutated
 */
void
DarwinAlgorithm::init_constraints()
{
  HP_STAT_AUTOSAVE(this->problem->darwinCallStats, "init_constraints");
  hp::Ids mutable_dish_ids = this->problem->dish_index->mutable_dish_ids;
  for (auto generic_constraint: this->problem->constraints)
    for (auto rule: generic_constraint->rules)
    {
      if (hp::has_in_common(rule->dish_ids, mutable_dish_ids))
        this->mutable_constraints[generic_constraint].push_back(rule);
    }
}

/*
 * Initialize the list of solutions with some
 * random ones / or the existing one
 */
void
DarwinAlgorithm::init_population()
{
  HP_STAT_AUTOSAVE(this->problem->darwinCallStats, "init_population");
  for (long i = 0; i < DarwinConfig::get<long>("population_size"); i++)
  {
    Solution *s;
    if (this->problem->initial_solution)
    {
      // existing solution, just copying it: this from where we're starting
      s = new Solution(*(this->problem->initial_solution));
    }
    else
      s = new Solution(this->problem);
    if (!(this->problem->stick_to_initial))
      s->init_from_favorites(); // We initialize the solution from favorite recipes and/or random recipes
    else
      s->randomize_out_of_domain(); // We randomize only the recipes that do not belong to their domain anymore
    ASSERT(s->get_nb_dishes(), "initialized solution is empty");
    this->population.push_back(s);
    ASSERT(s->isValid(), "Invalid initial population");
  }
}

void
DarwinAlgorithm::compute_population_variation() const {
  std::map<hp::Id, std::map<hp::Id, uint> > dish_type_recipe_usage; // { dish_type_id: { recipe_id: nb_repeat }}
  std::map<hp::Id, uint>                    dish_type_recipe_count; // { dish_type_id: nb_recipes }
  
  // Recipes of the best solution
  std::map<hp::Id, std::vector<long> > & rpdi = this->problem->darwinBestRecipesPerDishTypes;
  for (auto pair : this->population.front()->get_all_recipes()) {
    long dish_type_id = this->problem->dish_index->dish_type_per_dish_id[pair.first];
    for (RecipeData * recipe: pair.second) {
      auto result = std::find(rpdi[dish_type_id].begin(), rpdi[dish_type_id].end(), recipe->recipe_id);
      if (result == rpdi[dish_type_id].end()) {
        rpdi[dish_type_id].push_back(recipe->recipe_id);
      }
    }
  }
  // Security
  if (this->population.size() <= 1) {
    return;
  }
  // Recipes of the whole population
  for (Solution * individual: this->population) {
    for (auto pair: individual->get_all_recipes()) {
      long dish_type_id = this->problem->dish_index->dish_type_per_dish_id[pair.first];
      for (RecipeData * recipe: pair.second) {
        dish_type_recipe_usage[dish_type_id][recipe->recipe_id] += 1;
        dish_type_recipe_count[dish_type_id] += 1;
      }
    }
  }
  // Saving results in problem
  for (auto pair: dish_type_recipe_usage) {
    long    dish_type_id = pair.first;
    double  nb_recipes_per_solution = dish_type_recipe_count[dish_type_id] / this->population.size();
    long    nb_different_recipes = pair.second.size();
    long    score = (nb_different_recipes - nb_recipes_per_solution) * 100 / nb_recipes_per_solution;
    this->problem->darwinPopulationVariationScore[dish_type_id] = score;
  }
}
