#ifndef HIPPOCRATE_DARWIN_SELECTION_H_
# define HIPPOCRATE_DARWIN_SELECTION_H_

# include "hippocrate/controls/algorithm/darwin/types.h"

class DarwinSelection
{
public:
  DarwinSelection(hp::darwin::Population &_population,
                  hp::darwin::PopulationScores &_scores);
  virtual ~DarwinSelection() {}

  virtual void select() = 0;
protected:
  hp::darwin::Population        &population;
  hp::darwin::PopulationScores  &scores;
  uint                          population_size;
};

class Elitism : public DarwinSelection
{
public:
  Elitism(hp::darwin::Population &_population,
          hp::darwin::PopulationScores &_scores):
             DarwinSelection(_population, _scores) {}

  virtual void select() override final;
};

class RankProportionateSelection : public DarwinSelection
{
public:
  RankProportionateSelection(hp::darwin::Population &_population,
                             hp::darwin::PopulationScores &_scores):
             DarwinSelection(_population, _scores) {}

  virtual void select() override final;
};

/*
** Todo:
** - Vérifier le bon fonctionnement de la sélection (test powa)
** - Comparer les performances à RankProportionateSelection
** - Comparer la qualité à Elitism avec une valeure 'nb_elites' > 1
*/
class RankedRandomSelection : public DarwinSelection
{
public:
  explicit      RankedRandomSelection(hp::darwin::Population &_population, hp::darwin::PopulationScores &_scores, uint nb_elites = 1) :
                                      DarwinSelection(_population, _scores), nb_elites(nb_elites) {}

  virtual void  select() override final;
  uint          nb_elites;
};

#endif