
#include <boost/python.hpp>
#include <iostream>
#include "hippocrate/wrapstd.h"
#include "hippocrate/models/constraints/constraint.h"
#include "hippocrate/models/solution.h"
#include "hippocrate/models/problem.h"


std::ostream & operator << (std::ostream & stream, const Rule & c)
{
  stream << c.description();
  return stream;
}


/*
 * Add a dish set constraint
 */
void
GenericConstraint::add_rule(Rule *rule)
{
  this->rules.push_back(rule);
}

/*
  * Fully evaluate the solution with this constraint (all subconstraints)
  */
long
GenericConstraint::eval(const Solution *s, Score *sc) const
{
  long constraint_score = 0;
  for(auto rule: this->rules)
  {
    long rule_score = rule->eval(s);
    // ASSERT(rule_score >= 0, "Constraint score shouldn't be negative like", rule_score, "(", rule->description(), ")");
    
    sc->by_rule_id[rule->id] = rule_score;
    constraint_score += rule_score;
  }
  sc->by_constraint_id[this->id] = constraint_score;
  return constraint_score;
}

void
GenericConstraint::clear()
{
  for (auto rule: this->rules)
    delete rule;
}

GenericConstraint::~GenericConstraint()
{
  this->clear();
}

Rule::Rule(const DishIndex *di, hp::Ids d) : dish_ids(d)
{
  this->mutable_dish_ids = hp::intersect(di->mutable_dish_ids, d);
}


void    export_base_constraints()
{
  using namespace boost::python;

  class_<Rule, Rule*, boost::noncopyable>("Rule", no_init)
     .def_readonly("id", &Rule::id)
     .def("description", &Rule::description);
     
  class_< std::vector<Rule *> >("RuleVector")
      .def(vector_indexing_suite< std::vector<Rule *> >() );

  class_<GenericConstraint, boost::noncopyable>("GenericConstraint", no_init)
     .def_readonly("id", &GenericConstraint::id)
     .def_readonly("rules", &GenericConstraint::rules)
     .def("description", &GenericConstraint::description)
     .def("set_id", &GenericConstraint::set_id);
}