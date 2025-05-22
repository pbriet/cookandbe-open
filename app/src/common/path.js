export function recipePath(recipe) {
  return "/recettes/recette-" + recipe.urlKey;
}

export function recipeEditPath(recipe) {
  return "/recettes/" + recipe.id + "/edit/";
}
