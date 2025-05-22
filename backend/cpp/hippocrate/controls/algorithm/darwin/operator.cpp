
# include "hippocrate/controls/algorithm/darwin/darwin.h"
# include "hippocrate/controls/algorithm/darwin/operator.h"
# include "hippocrate/models/problem.h"

const Rule *
GeneticOperator::pick_proportional_constraint(const Solution * individual, bool filter_large_constraints) const
{
  // Picking a constraint in individual, with a chance proportional to its cost.
  std::map<const Rule *, long>   rule_scores;

  for (auto generic_constraint_pair: this->algorithm->mutable_constraints)
    for (auto rule: generic_constraint_pair.second)
    {
      if (filter_large_constraints && rule->dish_ids.size() > individual->get_nb_dishes() / 2)
        continue;
      long  rule_score = this->algorithm->scores[individual]->by_rule_id[rule->id];

      if (rule_score <= 0 || rule->dish_ids.size() == individual->get_nb_dishes())
        continue;
      rule_scores[rule] = rule_score;
    }
  if (rule_scores.size() <= 0)
    return nullptr;
  return RandomGenerator::pick_distrib_value(rule_scores);
}

const Rule *
GeneticOperator::pick_highest_constraint(const Solution * individual, bool filter_large_constraints) const
{
  // Picking highest constraint in individual
  const Rule * cross_constraint  = nullptr;
  long         best_score        = 10e9;

  for (auto generic_constraint_pair: this->algorithm->mutable_constraints)
    for (auto rule: generic_constraint_pair.second)
    {
      if (filter_large_constraints && rule->dish_ids.size() > individual->get_nb_dishes() / 2)
        continue;
      long  rule_score = this->algorithm->scores[individual]->by_rule_id[rule->id];

      if (rule_score <= 0 || rule_score >= best_score || rule->dish_ids.size() == individual->get_nb_dishes())
        continue;
      cross_constraint  = rule;
      best_score        = rule_score;
    }
  return cross_constraint;
}


/*
 * Simplified version of find_weakness
 * -> Just pick a rule given its score.
 * -> And a random dish in it
 */
// Weakness
// GeneticOperator::find_weakness(const Solution * individual)
// {
//   Score * score = this->algorithm->scores[individual];
//   ASSERT(score->total > 0, "Cannot apply oriented alteration on a solution with score == 0");
//
//   // We retrieve the score per rule
//   std::map<const Rule*, long> rule_scores;
//   for (auto iterator: this->algorithm->mutable_constraints)
//   {
//     const GenericConstraint *constraint = iterator.first;
//     if (score->by_constraint_id[constraint->id] > 0)
//       for (auto rule: constraint->rules)
//       {
//         long rule_score = score->by_rule_id[rule->id];
//         if (rule_score > 0 && rule->mutable_dish_ids.size() > 0)
//           rule_scores[rule] = rule_score;
//       }
//   }
//
//   if (rule_scores.size() == 0)
//     return Weakness(0, RandomGenerator::pick(this->algorithm->problem->dish_index->mutable_dish_ids));
//
//   // Select a random rule
//   const Rule* rule = RandomGenerator::pick_distrib_value(rule_scores);
//
//   // Select a random dish
//   long dish_id = RandomGenerator::pick(rule->mutable_dish_ids);
//   ASSERT(dish_id >= 0, "negative dish id in find_weakness");
//
//   return Weakness(rule, dish_id);
// }



/*
 * In a oriented crossover/mutation, the first stage is to select
 * which dish on which constraint we want to improve on a given solution
 */
Weakness
GeneticOperator::find_weakness(const Solution * individual)
{
  Score * score = this->algorithm->scores[individual];
  ASSERT(score->total > 0, "Cannot apply oriented alteration on a solution with score == 0");

  // We calculate the cost of scores per dish
  hp::darwin::DishScores dish_scores;

  for (auto generic_constraint_pair: this->algorithm->mutable_constraints)
    for (auto rule: generic_constraint_pair.second)
      {
        long rule_score_value = score->by_rule_id[rule->id];
        if (rule_score_value)
        {
          for (auto dish_id: rule->dish_ids)
            dish_scores[dish_id].add_rule(*(individual->problem), rule, rule_score_value);
        }
      }

  // And select one of the most expensive ones
  std::map<long, long> dish_id_to_score;
  long total_mutable_score = 0;
  for (auto dish_id: this->algorithm->problem->dish_index->mutable_dish_ids)
  {
    total_mutable_score += dish_scores[dish_id].score;
    dish_id_to_score[dish_id] = dish_scores[dish_id].score;
  }

  if (total_mutable_score <= 0)
    // There is no broken constraint on the dishes that can be mutated.
    return Weakness(0, RandomGenerator::pick(this->algorithm->problem->dish_index->mutable_dish_ids));


  long dish_id = RandomGenerator::pick_distrib_value(dish_id_to_score, total_mutable_score);
  ASSERT(dish_id >= 0, "negative dish id in find_weakness");

  if (dish_scores[dish_id].score <= 0)
    return Weakness(0, RandomGenerator::pick(this->algorithm->problem->dish_index->mutable_dish_ids));

  // Finally pick a random constraint within this dish
  ASSERT(dish_scores[dish_id].score > 0, "empty broken constraints");
  uint rule_id = RandomGenerator::pick_distrib_value(dish_scores[dish_id].cost_by_rule_id, dish_scores[dish_id].score);
  Rule * rule = individual->problem->rules_by_id[rule_id];

  return Weakness(rule, dish_id);
}
