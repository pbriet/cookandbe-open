
# include "hippocrate/controls/algorithm/darwin/darwin.h"
# include "hippocrate/controls/algorithm/darwin/logger.h"
# include "hippocrate/controls/algorithm/darwin/mutations/mutation.h"
# include "hippocrate/models/problem.h"

/*
 * Apply a random mutation to a solution
 */
int
RandomMutation::mutate(const Solution * individual)
{
  Solution * mutant = new Solution(*individual);

  // Retrieving which dish to mutate
  long dish_id_to_mutate = RandomGenerator::pick(this->algorithm->problem->dish_index->mutable_dish_ids);

  // Get a random recipe for this dish
  mutant->randomize_dish(dish_id_to_mutate);
  ASSERT(mutant->isValid(true), "Invalid mutated solution (random)");
  this->algorithm->children.push_back(mutant);
  return 1;
}

int
ScoreOrientedMutation::mutate(const Solution * individual)
{
  Solution * mutant = new Solution(*individual);
  
  DARWIN_LOG("Migrating (oriented) solution ", individual, "  --> score=", this->algorithm->scores[individual]->total);

  // Applying
  Weakness weakness = this->find_weakness(individual);
  if (weakness.rule)
    DARWIN_LOG("Improving rule ", *(weakness.rule), " with cost = ", weakness.rule->eval(mutant));
  if (weakness.rule != 0 && weakness.rule->improve_solution(mutant, weakness.dish_id))
    DARWIN_LOG("Improved value : ", weakness.rule->eval(mutant));
  else
    // Get a random recipe for this dish
    mutant->randomize_dish(weakness.dish_id);

#ifndef NDEBUG
  Score * mutant_score = this->algorithm->problem->eval(mutant, false);
  DARWIN_LOG("New solution score is ", mutant_score->total);
  delete mutant_score;
# endif
  ASSERT(mutant->isValid(true), "Invalid mutated solution (oriented)");
  this->algorithm->children.push_back(mutant);
  return 1;
}
