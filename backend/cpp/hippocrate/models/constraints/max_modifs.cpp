
#include "hippocrate/models/constraints/max_modifs.h"
#include "hippocrate/models/solution.h"

/*
 * Creates one unique constraint on all dishes
 */
void
MaxModifsConstraint::init_rules(DishIndex * dish_index)
{
  this->dish_index = dish_index;
  this->add_rule(new MaxModifsRule(dish_index, this, dish_index->all_dish_ids));
}


/*
 * Returns the number of modification of one solution comparing to the initial one
 */
long
MaxModifsConstraint::nb_modifs(const Solution *s) const
{
  long res = 0;

  if (this->day_id <= 0) {
    // All week mode
    for (auto dish_recipe: *s) {
      if (this->initial_solution->get_recipe_list(dish_recipe.first) != dish_recipe.second) {
        res += 1;
      }
    }
  } else {
    // Single day mode
    for (auto dish_id: this->dish_index->dish_ids_per_day.at(this->day_id)) {
      // Testing if for one given dish, recipes are the same
      if (this->initial_solution->get_recipe_list(dish_id) != s->get_recipe_list(dish_id)) {
        res += 1;
      }
    }
  }
  return res;
}

long
MaxModifsRule::eval(const Solution *s) const
{
  long nb_modifs = this->parent->nb_modifs(s);
  
  if (nb_modifs <= this->parent->max_modifs)
    return 0; // Less modifications than max allowed
    
  return (nb_modifs - this->parent->max_modifs) * this->parent->cost_per_modif;
};

void export_max_modifs_constraint()
{
    using namespace boost::python;

    class_< MaxModifsConstraint, MaxModifsConstraint *, boost::noncopyable, bases<GenericConstraint> >(
        "MaxModifsConstraint", init<Solution *, long, long, long>(
          (arg("solution"), arg("max_modifs"), arg("cost_per_modif"), arg("day_id") = 0)
        )
      )
      .def_readonly("day_id", &MaxModifsConstraint::day_id)
      .def("nb_modifs", &MaxModifsConstraint::nb_modifs)
    ;
}