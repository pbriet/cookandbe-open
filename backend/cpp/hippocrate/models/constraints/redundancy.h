#ifndef CONSTRAINT_REDUNDANCY_H_
# define CONSTRAINT_REDUNDANCY_H_

# include "hippocrate/tools/types.h"
# include "hippocrate/models/constraints/constraint.h"



/*
 * Constraint that encourages redundancy of recipes on a given dish type
 */
class RedundancyConstraint : public GenericConstraint
{
public:
  // Constructor
  RedundancyConstraint(long _cost_per_missing_portion, hp::Ids _dish_type_ids, long _optimal_nb_portions):
    GenericConstraint(),
    cost_per_missing_portion(_cost_per_missing_portion),
    dish_type_ids(_dish_type_ids),
    optimal_nb_portions(_optimal_nb_portions) {}

  // Initialize sub constraints
  virtual void              init_rules(DishIndex * dish_index) override;

  // Penalty per recipe which is under the optimal number of redundancies
  long                      cost_per_missing_portion;

  virtual std::string       description() const override { return "Redundancy"; }
  hp::Ids                   get_weak_dishids(Solution *s) const;

  hp::Ids                   dish_type_ids;

protected:
  long                      optimal_nb_portions;
};


/*
 * One unique constraint
 */
class RedundancyRule : public Rule
{
public:
  typedef                std::map<const RecipeData *, double> RecipePortionCount;

  virtual long           eval(const Solution *s) const override;
  virtual std::string    description(bool detailed=true) const override  { return "Redundancy"; }

  RedundancyRule(const DishIndex *di, RedundancyConstraint *_parent,
                              hp::Ids d, long _optimal_nb_portions): Rule(di, d),
                                                                     parent(_parent),
                                                                     optimal_nb_portions (_optimal_nb_portions){}

  virtual bool           improve_solution(Solution *s, long dish_id) const override;
  hp::Ids                get_weak_dishids(Solution *s) const;

protected:
  const RedundancyConstraint    *parent;
  long                          optimal_nb_portions;
  inline RecipePortionCount     recipe_portion_count(const Solution *s) const;
};

void export_redundancy_constraint();

#endif