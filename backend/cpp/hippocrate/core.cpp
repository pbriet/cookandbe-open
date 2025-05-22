#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <exception>
#include <iostream>

#include "hippocrate/wrapstd.h"
#include "hippocrate/tools/random.h"
#include "hippocrate/tools/debug.h"
#include "hippocrate/tools/container.h"
#include "hippocrate/tools/stats.h"
#include "hippocrate/models/dataindexer.h"
#include "hippocrate/models/dish.h"
#include "hippocrate/models/recipe.h"
#include "hippocrate/models/dishrecipe.h"
#include "hippocrate/models/recipeindex.h"
#include "hippocrate/models/dishindex.h"
#include "hippocrate/models/problem.h"
#include "hippocrate/models/solution.h"
#include "hippocrate/models/score.h"
#include "hippocrate/models/constraints/budget.h"
#include "hippocrate/models/constraints/constraint.h"
#include "hippocrate/models/constraints/interval.h"
#include "hippocrate/models/constraints/nutrient.h"
#include "hippocrate/models/constraints/nutrient_balance.h"
#include "hippocrate/models/constraints/unicity.h"
#include "hippocrate/models/constraints/redundancy.h"
#include "hippocrate/models/constraints/meal_balance.h"
#include "hippocrate/models/constraints/meal_type_balance.h"
#include "hippocrate/models/constraints/max_modifs.h"
#include "hippocrate/models/constraints/recipes.h"
#include "hippocrate/models/constraints/time.h"
#include "hippocrate/models/constraints/shopping.h"
#include "hippocrate/models/filters/filter.h"
#include "hippocrate/controls/algorithm/darwin/config.h"

void translate_exception(std::exception const& e)
{
  // Use the Python 'C' API to set up an exception object
  static std::string   message = e.what();
  PyErr_SetString(PyExc_RuntimeError, message.c_str());
}

BOOST_PYTHON_MODULE(core)
{
  using namespace boost::python;
  register_exception_translator<std::exception>(&translate_exception);

  export_std();

  export_base_constraints();
  export_budget_constraint();
  export_darwin_config();
  export_data_indexer();
  export_dish();
  export_dish_index();
  export_dish_type_index();
  export_dishrecipe();
  export_food_index();
  export_interval_rule();
  export_max_modifs_constraint();
  export_meal_balance_constraint();
  export_meal_type_balance_constraint();
  export_nutrient_balance_constraint();
  export_nutrient_constraint();
  export_problem();
  export_recipe_data();
  export_recipe_filters();
  export_recipes_constraints();
  export_redundancy_constraint();
  export_score();
  export_shopping_constraint();
  export_solution();
  export_time_constraint();
  export_tools();
  export_tools_stats();
  export_unicity_constraint();
}
