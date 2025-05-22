#ifndef HIPPOCRATE_MODELS_CONSTRAINTS_RECIPES_H_
# define HIPPOCRATE_MODELS_CONSTRAINTS_RECIPES_H_

# include "hippocrate/models/constraints/constraint.h"
# include "hippocrate/tools/types.h"

/*
 * Constraint on budget
 */
class RecipesPenaltiesConstraint : public GenericConstraint
{
public:
  typedef std::map<hp::Id, float>     PenaltiesDict;
  // Constructor
  RecipesPenaltiesConstraint() :
          GenericConstraint() {};

  // Initialize sub constraints
  virtual void              init_rules(DishIndex * dish_index) override;

  virtual std::string       description() const override { return "RecipesPenaltiesConstraint"; }

  void                      add_penalty(hp::Id recipe_id, float penalty);

  // Max average budget per dish
  RecipesPenaltiesConstraint::PenaltiesDict            penalties_dict;
};



class RecipesPenaltiesRule : public Rule
{
public:
  RecipesPenaltiesRule(
    const DishIndex * di,
    hp::Ids           dish_ids,
    RecipesPenaltiesConstraint::PenaltiesDict &_penalties_dict
  ):
    Rule(di, dish_ids),
    penalties_dict(_penalties_dict)
  {}

  virtual std::string       description(bool detailed=true) const override { return "RecipesPenaltiesRule"; }

  virtual long              eval(const Solution *s) const override;
  virtual void              on_solution_new_recipes(Solution *s, long dish_id) const override;
  virtual void              on_solution_rm_recipes(Solution *s, long dish_id)  const override;
  virtual bool              improve_solution(Solution *s, long dish_id) const override;

  RecipesPenaltiesConstraint::PenaltiesDict            &penalties_dict;
};

void export_recipes_constraints();

#endif // HIPPOCRATE_MODELS_CONSTRAINTS_RECIPES_H_