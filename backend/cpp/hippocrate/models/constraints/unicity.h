#ifndef CONSTRAINT_UNICITY_H_
# define CONSTRAINT_UNICITY_H_

# include "hippocrate/tools/types.h"
# include "hippocrate/models/constraints/constraint.h"

/*
 * Constraint on unicity of recipes
 */
class UnicityConstraint : public GenericConstraint
{
public:
  // Constructor
  UnicityConstraint(long _cost_per_duplicate) : cost_per_duplicate(_cost_per_duplicate) {}
  UnicityConstraint(long _cost_per_duplicate, hp::Ids _week_dish_type_ids, hp::Ids _day_dish_type_ids) :
    GenericConstraint(),
    cost_per_duplicate(_cost_per_duplicate),
    week_dish_type_ids(_week_dish_type_ids),
    day_dish_type_ids(_day_dish_type_ids) {}

  // Initialize sub constraints
  virtual void              init_rules(DishIndex * dish_index) override;
  long                      nb_redundancies(const Solution *s) const;

  // Penalty per recipe duplication
  long                      cost_per_duplicate;

  virtual std::string       description() const override { return "Unicity"; }

public:
  hp::Ids                   week_dish_type_ids;
  hp::Ids                   day_dish_type_ids;
};


/*
 * Unique dishset constraint on all meals, whatever the number of days
 */
class UnicityRule : public Rule
{
public:
  long           eval(const Solution *s) const override;
  long                   nb_redundancies(const Solution *s) const;
  std::string    description(bool detailed=true) const override  { return "Unique"; }

  UnicityRule(const DishIndex *di, UnicityConstraint *_parent,
                            hp::Ids d): Rule(di, d),
                                        parent(_parent) {}

protected:
  const UnicityConstraint    *parent;
};

/*
 * Avoiding having, within the same day, twice the same major ingredient.
 * The list of major ingredients to avoid is given in argument  (pastas, rice,
 */
class UnicityFoodTagConstraint : public GenericConstraint
{
public:
  // Constructor
  UnicityFoodTagConstraint(long _cost_per_duplicate, hp::Ids _food_tag_ids) :
    GenericConstraint(),
    cost_per_duplicate(_cost_per_duplicate),
    food_tag_ids(_food_tag_ids) {}

  // Initialize sub constraints
  virtual void              init_rules(DishIndex * dish_index) override;
  long                      nb_redundancies(const Solution *s) const;

  // Penalty per recipe duplication
  long                      cost_per_duplicate;

  virtual std::string       description() const override { return "Food tag unicity"; }

public:
  hp::Ids                   food_tag_ids;
};


/*
 * One food_tag unicity constraint per day
 */
class UnicityFoodTagDailyRule : public Rule
{
public:
  typedef                std::map<long, long> FoodTagOccurences;

  virtual long           eval(const Solution *s) const override;
  long                   nb_redundancies(const Solution *s) const;
  virtual std::string    description(bool detailed=true) const override  { return "Food tag unicity (daily)"; }

  UnicityFoodTagDailyRule(const DishIndex *di, UnicityFoodTagConstraint *_parent,
                                hp::Ids d, long _day_id): Rule(di, d),
                                                       day_id(_day_id), parent(_parent) {}

  long                    day_id;
protected:
  const UnicityFoodTagConstraint    *parent;
};



void export_unicity_constraint();

#endif