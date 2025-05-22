
# include "hippocrate/controls/algorithm/darwin/darwin.h"
# include "hippocrate/controls/algorithm/darwin/crossovers/crossover.h"
# include "hippocrate/models/problem.h"

/*
 * Apply a crossover of solution A and B, based on B, modifying only some dishes
 * By retrieving them from A
 */
Solution *
Crossover::cross_a_to_b(const Solution * a, const Solution * b, const Rule * cross_constraint)
{
  ASSERT(a != nullptr, "can't mate with a null father !");
  ASSERT(b != nullptr, "can't mate with a null father !");
  // Creating baby
  Solution  *baby = new Solution(*b);
  
  // Mating
  for (auto dish_id : cross_constraint->dish_ids)
    baby->set_recipe_list(dish_id, a->get_recipe_list(dish_id), a->get_total_recipe_ratio(dish_id), false);
  
  ASSERT(baby->isValid(true), "Invalid crossed solution");
  return baby;
}

int
Crossover::constraint_mating(const Solution * parent1, const Solution * parent2,
                             const Rule * cross_constraint, bool one_way_only)
{
  this->algorithm->children.push_back(this->cross_a_to_b(parent1, parent2, cross_constraint));
  if (one_way_only)
    return 1;

  this->algorithm->children.push_back(this->cross_a_to_b(parent2, parent1, cross_constraint));
  return 2;
}

const Solution *
Crossover::pick_best_mate(const Solution * parent1, const Rule * rule) const
{
  // Lets look for the best mate
  long                      best_score  = this->algorithm->scores[parent1]->by_rule_id[rule->id];
  const Solution *          best_mate   = nullptr;

  for (const Solution * parent2: this->algorithm->population)
  {
    if (parent2 == parent1)
      continue;

    long constraint_cost = this->algorithm->scores[parent2]->by_rule_id[rule->id];
    if (constraint_cost >= best_score)
      continue;
    best_mate  = parent2;
    best_score = constraint_cost;
  }
  return best_mate;
}


const Solution *
Crossover::pick_better_mate(const Solution * s, const Rule * rule) const
{
  long                      cost        = this->algorithm->scores[s]->by_rule_id[rule->id];
  hp::darwin::Population better_solutions(this->algorithm->population.size() - 1);

  uint i = 0;
  for (auto solution: this->algorithm->population)
    if (solution != s)
    {
      long solution_ctr_cost = this->algorithm->scores[solution]->by_rule_id[rule->id];
      if (solution_ctr_cost >= cost)
        continue;
      better_solutions[i] = solution;
      i++;
    }
  if (i == 0)
    return 0; // There is no better solution for this constraint

  better_solutions.resize(i);
  return RandomGenerator::pick(better_solutions);
}
  
int
RandomMateCrossover::cross(const Solution * parent1)
{
  // Random pick constraint
  const hp::darwin::RuleList   & Rules  = RandomGenerator::pick_value(this->algorithm->mutable_constraints);
  const Rule                   * cross_constraint    = RandomGenerator::pick(Rules);
  if (cross_constraint->dish_ids.size() > parent1->get_nb_dishes() / 2)
    return 0;

  // Random pick crossover mate
  Solution  *parent2 = RandomGenerator::pick(this->algorithm->population);
  if (parent1 == parent2)
    return 0;

  return this->constraint_mating(parent2, parent1, cross_constraint);
}

int
ProportionalConstraintRandomMateCrossover::cross(const Solution * parent1)
{
  // Picking highest constraint in parent1
  const Rule * cross_constraint = this->pick_proportional_constraint(parent1, true);

  if (cross_constraint == nullptr)
    return 0;

  // Random pick crossover mate
  Solution  * parent2 = RandomGenerator::pick(this->algorithm->population);
  if (parent1 == parent2)
    return 0;
  
  return this->constraint_mating(parent1, parent2, cross_constraint, true);
}

int
ProportionalConstraintBetterMateCrossover::cross(const Solution * parent1)
{
  // Picking highest constraint in parent1
  const Rule * cross_constraint = this->pick_proportional_constraint(parent1, true);

  if (cross_constraint == nullptr)
    return 0;

  // Random pick crossover mate
  const Solution  * parent2 = this->pick_better_mate(parent1, cross_constraint);
  if (parent2 == nullptr)
    return 0;

  return this->constraint_mating(parent1, parent2, cross_constraint, true);
}

int
HighConstraintBestMateCrossover::cross(const Solution * parent1)
{
  // Picking highest constraint in parent1
  const Rule * cross_constraint = this->pick_highest_constraint(parent1, true);

  if (cross_constraint == nullptr)
    return 0;
  
  const Solution * parent2 = this->pick_best_mate(parent1, cross_constraint);
  if (parent2 == nullptr)
  {
    // No best mate, random pick
    parent2 = RandomGenerator::pick(this->algorithm->population);
    if (parent1 == parent2)
      return 0;
  }
  return this->constraint_mating(parent1, parent2, cross_constraint, true);
}
