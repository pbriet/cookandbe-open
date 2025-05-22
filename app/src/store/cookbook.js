import { each, includes, find, without } from "lodash";
import { recipeEditPath } from "@/common/path.js";
import router from "@/router";
import { DEFAULT_RECIPE_NAME } from "@/common/static.js";
import API from "@/api.js";

/*
 * Store managing the user cookbook
 */
export default {
  namespaced: true,
  state: {
    // Cookbook recipe ids (ids of recipe directly)
    cookbookRecipeIds: { values: [] },
    // CookbookRecipe objects
    cookbookRecipeObjects: { values: [] },
    // Personal recipes  (recipe ids)
    personalRecipeIds: { values: [] },
  },
  mutations: {},
  getters: {
    recipeIsPersonal: (state) => (recipeId) => {
      return includes(state.personalRecipeIds.values, recipeId);
    },
    recipeInCookbook: (state) => (recipeId) => {
      return includes(state.cookbookRecipeIds.values, recipeId);
    },
    /*
     * Returns true if recipe is either personal, or in cookbook
     */
    recipeIsFavorite: (state, getters) => (recipeId) => {
      return getters.recipeInCookbook(recipeId) || getters.recipeIsPersonal(recipeId);
    },
    nbRecipes(state) {
      return state.cookbookRecipeIds.values.length;
    },
  },
  actions: {
    update({ state, rootGetters }) {
      const userId = rootGetters["user/id"];
      let promise = API.cookbookRecipes(userId).then((data) => {
        state.cookbookRecipeObjects.values = data;
        state.cookbookRecipeIds.values = [];
        each(data, (cr) => {
          state.cookbookRecipeIds.values.push(cr.recipe);
        });
        return data;
      });
      state.cookbookRecipeObjects.$promise = promise;
      state.cookbookRecipeIds.$promise = promise;

      promise = API.recipe.personalRecipes(userId).then((data) => {
        state.personalRecipeIds.values = data.results;
      });
      state.personalRecipeIds.$promise = promise;
    },
    async createRecipe({ dispatch }, { userId, defaultName }) {
      if (!defaultName) {
        defaultName = DEFAULT_RECIPE_NAME;
      }
      const recipe = await new API.recipe.save({
        author: userId,
        description: "Décrivez ici votre recette",
        difficulty: 3,
        nbPeople: 4,
        price: 3,
        name: defaultName,
      });
      router.push(recipeEditPath(recipe));
      dispatch("update");
    },
    async addRecipe({ state, rootGetters }, recipeId) {
      const userId = rootGetters["user/id"];
      const newCookbookRecipe = await API.cookbookRecipe.save(userId, { userId, user: userId, recipe: recipeId });
      state.cookbookRecipeObjects.values.push(newCookbookRecipe);
      state.cookbookRecipeIds.values.push(recipeId);
      return true;
    },
    async rmRecipe({ state, rootGetters }, recipeId) {
      const userId = rootGetters["user/id"];
      const cookbookRecipe = find(state.cookbookRecipeObjects.values, ["recipe.id", recipeId]);
      state.cookbookRecipeObjects.values = without(state.cookbookRecipeObjects.values, cookbookRecipe);
      state.cookbookRecipeIds.values = without(state.cookbookRecipeIds.values, recipeId);
      await API.cookbookRecipe.deleteByRecipeId(userId, { userId, recipeId });
    },
    rmPersonalRecipe({ state, dispatch }, recipe) {
      if (!window.confirm("Cette opération n'est pas réversible ! Voulez-vous vraiment supprimer votre recette ?")) {
        return;
      }
      dispatch("recipe/deleteRecipe", recipe, { root: true });
      state.personalRecipeIds.values = without(state.personalRecipeIds.values, recipe.id);
    },
    async getRecipes({ state, dispatch }) {
      await state.cookbookRecipeIds.$promise;
      const values = await dispatch("recipe/getMany", state.cookbookRecipeIds.values, { root: true });
      return { values };
    },
    async getPersonalRecipes({ state, dispatch }) {
      await state.personalRecipeIds.$promise;
      const values = await dispatch("recipe/getMany", state.personalRecipeIds.values, { root: true });
      return { values };
    },
  },
};
