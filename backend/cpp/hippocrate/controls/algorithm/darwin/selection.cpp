#include <climits>
#include "hippocrate/controls/algorithm/darwin/selection.h"
#include "hippocrate/controls/algorithm/darwin/config.h"
#include "hippocrate/tools/random.h"
#include "hippocrate/tools/print.h"
#include "hippocrate/tools/exception.h"
#include <vector>

DarwinSelection::DarwinSelection(hp::darwin::Population &_population,
                                 hp::darwin::PopulationScores &_scores):
                        population(_population),
                        scores(_scores)
{
  this->population_size = DarwinConfig::get<long>("population_size");;
}

/*
 * Applies a "elitism" selection
 * Only keeping the N best scores
 */
void Elitism::select()
{
  if (this->population_size >= this->population.size())
    return; // Nothing to truncate

  for (uint i = this->population_size; i < this->population.size(); i++)
  {
    delete this->scores[this->population[i]];
    this->scores.erase(this->population[i]);
    delete this->population[i];
  }
  this->population.resize(this->population_size);
}

/*
 * Applies a "rank proportionate" selection
 * The higher your rank is, the higher the probability will be that you'll be selected
 */
void RankProportionateSelection::select()
{
  uint current_pop_size = this->population.size();
  if (this->population_size >= current_pop_size)
    return; // Nothing to truncate

  // sum(ranks) = 1 + 2 + 3 + .. + n = n(n+1) / 2
  ASSERT(current_pop_size < sqrt(ULONG_MAX), "Overflow in RankProportionateSelection");
  unsigned long ranks_sum = ((current_pop_size - 1) * current_pop_size) / 2;

  uint to_delete  = current_pop_size - this->population_size;
  
  // Removing the extra elements
  for (uint i = 0; i < to_delete; i ++)
  {
    // We add/remove one because we don't want the first solution to be deleted
    unsigned long to_delete_rank_agg =  1 + RandomGenerator::rand() % (ranks_sum - 1);
    // The formula to retrieve i from rank is  (solving agg=n(n+1)/2 with n as unknown)
    // sqrt(0.25 + 2*rank) -0.5
    uint j = ceil(sqrt(0.25 + 2 * to_delete_rank_agg) - 0.5);

    // Removing the element
    delete this->scores[this->population[j]];
    this->scores.erase(this->population[j]);
    delete this->population[j];
    for (uint k = j + 1; k < this->population.size(); k++)
      this->population[k - 1] = this->population[k];
    this->population.resize(this->population.size() - 1);

    // Updating rank sum
    ranks_sum -= current_pop_size--;
  }
  ASSERT(this->population.size() == this->population_size, "Rank selection failed");
}

/*
 * Applies a selection by processing draws on each element, with a probability based on the rank in the population.
 */
void RankedRandomSelection::select()
{
  uint              i, current_pop_size = this->population.size();
  uint              to_delete = current_pop_size - this->population_size;
  std::vector<uint> ids_to_delete(to_delete);

  if (this->population_size >= current_pop_size)
    return; // Nothing to truncate

  // Listing excluded elements
  for (i = current_pop_size - 1; true; --i)
  {
    if (RandomGenerator::rand() % (i + 1 - this->nb_elites) <= 2 * to_delete)
    {
      ids_to_delete[--to_delete] = i;
      // Removing the element
      delete this->scores[this->population[i]];
      this->scores.erase(this->population[i]);
      delete this->population[i];
    }
    if (to_delete == 0)
      break;
    ASSERT(i <= this->nb_elites, "to_delete should have break here");
  }
  // Removing the listed elements
  for (i = ids_to_delete[to_delete]; i < current_pop_size; ++i)
  {
    while (i + to_delete == ids_to_delete[to_delete])
    {
      ++to_delete;
      ASSERT((to_delete < ids_to_delete.size()), "'to_delete' index out of range");
      ASSERT((i + to_delete < current_pop_size), "'i' index out of range");
    }
    this->population[i] = this->population[i + to_delete];
  }
  this->population.resize(this->population.size() - 1);
  ASSERT(this->population.size() == this->population_size, "Rank selection failed");
}
