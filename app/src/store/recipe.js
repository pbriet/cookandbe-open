import API from "@/api.js";
import router from "@/router";
import { find } from "lodash";
import { RECIPE_STATUS } from "@/common/static.js";

/*
 * Lazy loading of recipes
 */
export default {
  namespaced: true,
  state: {
    recipeById: {}, // With ingredients and a given ratio: {recipe_id: {ratio: value
    recipeSummaryById: {}, // Short version (photo, minutes, title, ...)
    recipeNutrientsById: {},
    recipeByKey: {}, // With full ingredients, and default ratio
  },
  getters: {
    get: (state) => (recipeId, ratio) => {
      if (!recipeId) {
        console.log("error: no recipe for null recipeId");
        return null;
      }
      let recipe = state.recipeById[recipeId];
      if (recipe) {
        recipe = recipe[ratio];
      }
      if (recipe) {
        return recipe;
      }
      return null;
    },
    isPublished: () => (recipe) => {
      return recipe.status >= find(RECIPE_STATUS, ["label", "Publiée"]).id;
    },
    canEdit: (_, getters) => (user, recipe) => {
      if (!recipe || !user) {
        return false;
      }
      return (recipe.authorId == user.id || recipe.author == user.id) && !getters.isPublished(recipe);
    },
  },
  mutations: {
    /*
     * Delete the cached values for a given recipe
     * To call when a recipe is modified
     */
    clearCached(state, recipeId) {
      delete state.recipeNutrientsById[recipeId];
      delete state.recipeSummaryById[recipeId];
      delete state.recipeById[recipeId];
      for (let key in state.recipeByKey) {
        if (state.recipeByKey[key].id == recipeId) {
          delete state.recipeByKey[key];
          break;
        }
      }
    },
    /*
     * Store the recipe in memory (js cache)
     */
    storeRecipe(state, { recipeId, ratio, recipe }) {
      if (!state.recipeById[recipeId]) {
        state.recipeById[recipeId] = {};
      }
      state.recipeById[recipeId][ratio] = recipe;
    },
  },
  actions: {
    /*
     * Load a list of recipes, with one query only.
     * Only if they're not loaded already (doesn't update pre-loaded values)
     */
    async loadMany({ state, commit }, recipeIds) {
      const BATCH_LENGTH = 50;
      const notLoadedIds = [];
      for (const recipeId of recipeIds) {
        if (!state.recipeById[recipeId] || !state.recipeById[recipeId][undefined]) {
          notLoadedIds.push(recipeId);
        }
      }
      if (notLoadedIds.length === 0) {
        return;
      } else {
        // Loading by batch of 50 recipes
        let batch = 0;
        var promises = [];
        while (batch * BATCH_LENGTH < notLoadedIds.length) {
          // Preparing a batch
          const queryIds = [];
          for (let j = batch * BATCH_LENGTH; j < Math.min((batch + 1) * BATCH_LENGTH, notLoadedIds.length); j++) {
            queryIds.push(notLoadedIds[j]);
          }
          // Querying
          promises.push(
            API.recipe.getMany({ ids: queryIds, serializer: "full" }).then((recipes) => {
              for (const recipe of recipes) {
                commit("storeRecipe", { recipeId: recipe.id, ratio: undefined, recipe });
              }
            })
          );
          // Next batch
          batch += 1;
        }
        await Promise.all(promises);
      }
    },
    /*
     * Returns a list of recipes from ids
     */
    async getMany({ getters, dispatch }, recipeIds) {
      const values = [];
      await dispatch("loadMany", recipeIds);
      for (const recipeId of recipeIds) {
        values.push(getters.get(recipeId));
      }
      return values;
    },
    /*
     * Get a summary of the recipe (no ingredients)
     */
    async getSummary({ state }, recipeId) {
      const recipe = state.recipeSummaryById[recipeId];
      if (recipe) {
        return recipe;
      }
      state.recipeSummaryById[recipeId] = await API.recipe.get(recipeId, { include_internal: true });
      return state.recipeSummaryById[recipeId];
    },
    /*
     * Get the nutrients values of a recipe
     */
    async getNutrients({ state }, { recipeId, ratio }) {
      if (!ratio) {
        ratio = 1;
      }
      const recipeNutrients = state.recipeNutrientsById[recipeId];
      if (recipeNutrients && recipeNutrients[ratio]) {
        return recipeNutrients[ratio];
      }
      if (!state.recipeNutrientsById[recipeId]) {
        state.recipeNutrientsById[recipeId] = {};
      }
      state.recipeNutrientsById[recipeId][ratio] = await API.recipe.nutrients(recipeId, {
        include_internal: true,
        ratio,
      });
      return state.recipeNutrientsById[recipeId][ratio];
    },
    /*
     * Return, with no caching, the ratings of a recipe
     */
    getRatings(_, { recipeId, offset, limit }) {
      return API.recipe.ratings(recipeId, { offset, limit });
    },
    /*
     * Get the recipe with its ingredients, given a ratio (can be null)
     */
    async getRecipe({ getters, dispatch }, { recipeId, ratio }) {
      const recipe = getters.get(recipeId, ratio);
      if (recipe) {
        return recipe;
      }
      return await dispatch("loadRecipe", { recipeId, ratio });
    },
    /*
     * From a recipe key (SEO-optimized)
     * returns the recipe with default ratio
     */
    async getFromKey({ state, dispatch }, recipeKey) {
      const recipe = state.recipeByKey[recipeKey];
      if (recipe) {
        return recipe;
      }
      return await dispatch("loadRecipeFromKey", { recipeKey });
    },
    /*
     * Retrieve the recipe from server
     */
    async loadRecipe({ commit }, { recipeId, ratio }) {
      const queryDict = { include_internal: true };
      if (ratio) {
        queryDict.ratio = ratio;
      }
      const recipe = await API.recipe.withIngredients(recipeId, queryDict);
      commit("storeRecipe", { recipeId, ratio, recipe });
      return recipe;
    },
    async loadRecipeFromKey({ state }, { recipeKey }) {
      const data = await API.recipe.fromKey(recipeKey);
      if (data.exists) {
        state.recipeByKey[recipeKey] = data;
      }
      return data;
    },
    async deleteRecipe(_, recipe) {
      await API.recipe.remove(recipe.id);
      router.push({ name: "Cookbook" });
    },
  },
};
