#include <boost/python.hpp>
#include <boost/python/return_value_policy.hpp>
#include "hippocrate/wrapstd.h"
#include "hippocrate/models/problem.h"
#include "hippocrate/models/score.h"
#include "hippocrate/models/constraints/constraint.h"


/*
 * Allocate the correct size to the score vectors
 */
Score::Score(const Problem &p)
{
  this->by_constraint_id.resize(p.constraints.size());
  this->by_rule_id.resize(p.rules_by_id.size());
}

void DishScore::allocate(const Problem &p)
{
  this->cost_by_rule_id.resize(p.rules_by_id.size(), 0);
  this->initialized = true;
}

/*
 * Cumulate one constraint score on a given dish
 */
void DishScore::add_rule(const Problem &p, const Rule *rule, long score)
{
  if (!this->initialized)
    this->allocate(p);
  this->cost_by_rule_id[rule->id] = score;
  this->score += score;
}

void export_score()
{
  using namespace boost::python;

  class_<Score>("Score", no_init)
   .def_readonly("total",   &Score::total)
   .def_readonly("by_constraint_id",   &Score::by_constraint_id)
   .def_readonly("by_rule_id",         &Score::by_rule_id);
   
}