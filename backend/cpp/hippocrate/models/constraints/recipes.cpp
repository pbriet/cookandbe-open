#include "hippocrate/models/constraints/recipes.h"
#include "hippocrate/models/solution.h"

void
RecipesPenaltiesConstraint::init_rules(DishIndex * dish_index)
{
    this->add_rule(new RecipesPenaltiesRule(dish_index, dish_index->mutable_dish_ids, this->penalties_dict));
}


void
RecipesPenaltiesConstraint::add_penalty(hp::Id recipe_id, float penalty)
{
  if (this->penalties_dict.count(recipe_id) == 0)
      this->penalties_dict[recipe_id] = 0;
  this->penalties_dict[recipe_id] += penalty;
}

long
RecipesPenaltiesRule::eval(const Solution *s) const
{
   if (s->constraint_buffer.count(this) == 0)
      return 0;
  return s->constraint_buffer.at(this);
}

void
RecipesPenaltiesRule::on_solution_new_recipes(Solution *s, long dish_id) const
{
  for (const RecipeData * recipe : s->get_recipe_list(dish_id)) {
    if (this->penalties_dict.count(recipe->recipe_id))
        s->constraint_buffer[this] += this->penalties_dict.at(recipe->recipe_id);
  }
}

void
RecipesPenaltiesRule::on_solution_rm_recipes(Solution *s, long dish_id)  const
{
  for (const RecipeData * recipe : s->get_recipe_list(dish_id)) {
    if (this->penalties_dict.count(recipe->recipe_id))
        s->constraint_buffer[this] -= this->penalties_dict.at(recipe->recipe_id);
  }
}

bool
RecipesPenaltiesRule::improve_solution(Solution *s, long dish_id) const
{
  // Index of the dishrecipe to change  (the biggest cost)
  int dish_recipe_no_to_change = 0;
  float biggest_penalty = 0;

  int i = 0;
  for (const RecipeData * recipe : s->get_recipe_list(dish_id))
  {
    if (this->penalties_dict.count(recipe->recipe_id))
    {
      float penalty = this->penalties_dict.at(recipe->recipe_id);
      if (penalty > biggest_penalty) {
        biggest_penalty = penalty;
        dish_recipe_no_to_change = i;
      }
    }
    i += 1;
  }

  if (biggest_penalty == 0)
      return false;

  // Changing the dishrecipe by a random one
  s->randomize_dishrecipe(dish_id, dish_recipe_no_to_change);
  return true;
}



/*
 * Exposes functions/class/methods to Python
 */
void export_recipes_constraints()
{
  using namespace boost::python;

  class_<RecipesPenaltiesConstraint, RecipesPenaltiesConstraint *, boost::noncopyable, bases<GenericConstraint> >(
      "RecipesPenaltiesConstraint", init<>()
    )
    .def("add_penalty",                  &RecipesPenaltiesConstraint::add_penalty)
  ;

  class_<RecipesPenaltiesRule, boost::noncopyable, bases<Rule> >("RecipesPenaltiesRule", no_init)
  ;

}
