import API from "@/api.js";
import { find } from "lodash";

function _getUstensilWarnings(store, warnings, recipe) {
  const ustensils = store.rootGetters["equipment/getUstensils"];
  const missingUstensils = [];
  for (const recipeUstensilId of recipe.ustensils) {
    let compatible = false;

    for (const ustensilId of store.state.userUstensils) {
      if (recipeUstensilId === ustensilId) {
        compatible = true;
        break;
      }
    }
    if (!compatible) {
      missingUstensils.push(find(ustensils, ["id", recipeUstensilId]).name);
    }
  }
  if (missingUstensils.length) {
    let message = "Cette recette nécessite ";
    if (missingUstensils.length === 1) {
      message += "l'équipement suivant:";
    } else {
      message += "les équipements suivants:";
    }
    message += " <b>" + missingUstensils.join(", ") + "</b>.";
    warnings.push(_createWarning(2, message, "Modifier mes ustensiles", { name: "EquipmentConfig" }));
  }
}

function _getTasteWarnings(store, warnings, recipe) {
  if (!recipe.foodTags) {
    return;
  }
  const mayDislike = [];
  for (const recipeFoodTagId of recipe.foodTags) {
    for (const taste of store.state.userTastes) {
      if (recipeFoodTagId === taste.foodTag.id) {
        mayDislike.push(taste.foodTag.name);
      }
    }
  }
  if (mayDislike.length) {
    warnings.push(
      _createWarning(
        1,
        "Vous risquez de ne pas aimer cette recette car elle contient: <b>" + mayDislike.join(", ") + "</b>",
        "Modifier mes goûts",
        { name: "TastesConfig" }
      )
    );
  }
}

function _getDislikedRecipeWarnings(store, warnings, recipe) {
  if (store.getters.isDisliked(recipe.id)) {
    warnings.push(_createWarning(1, "Vous avez indiqué ne pas aimer cette recette."));
  }
}

function _getDietExclusionWarnings(store, warnings, recipe) {
  if (!recipe.foodTags) {
    return;
  }
  const mustExclude = [];
  const mayExclude = [];
  const dietExclusions = store.rootGetters["diet/getDietExclusions"];
  const dietWarnings = store.rootGetters["diet/getDietWarnings"];

  for (const recipeFoodTagId of recipe.foodTags) {
    for (const excludedFoodTag of dietExclusions) {
      if (recipeFoodTagId === excludedFoodTag.id) {
        mustExclude.push(excludedFoodTag.name);
      }
    }

    for (const forewarnedFoodTag of dietWarnings) {
      if (recipeFoodTagId === forewarnedFoodTag.id) {
        mayExclude.push(forewarnedFoodTag.name);
      }
    }
  }
  if (mustExclude.length) {
    warnings.push(
      _createWarning(
        3,
        "Cette recette contient des éléments incompatibles avec votre alimentation: <b>" +
          mustExclude.join(", ") +
          "</b>"
      )
    );
  } else if (mayExclude.length) {
    warnings.push(_createWarning(1, "Certains ingrédients de cette recette peuvent contenir des traces de gluten."));
  }
}

function _getUserSettingWarnings(store, warnings, recipe) {
  const kalooEffect = 2; // "Parce que sinon c'est un peu extrême" (c) Kaloo
  if (recipe.price > store.state.userSettings.budget + kalooEffect) {
    warnings.push(
      _createWarning(1, "Cette recette est indiquée comme étant chère à réaliser.", "Modifier mes réglages", {
        name: "OtherConfig",
      })
    );
  }
}

function _createWarning(level, htmlMessage, actionCaption, actionUrl) {
  const levelIcons = [
    ["fas", "info-circle"],
    ["fas", "exclamation-triangle"],
    ["fas", "ban"],
  ];

  return {
    level: level,
    icon: levelIcons[level - 1],
    htmlMessage,
    actionCaption,
    actionUrl,
  };
}

export default {
  namespaced: true,
  state: {
    userUstensils: [],
    userTastes: [],
    dislikedRecipes: [],
    userSettings: {},
  },
  getters: {
    isDisliked: (state) => (recipeId) => {
      return find(state.dislikedRecipes, ["recipe", recipeId]);
    },
    getWarnings: (state, getters, rootState, rootGetters) => (recipeId) => {
      if (!recipeId) {
        return null;
      }

      const recipe = rootGetters["recipe/get"](recipeId);
      if (!recipe) {
        return null;
      }

      const store = { state, getters, rootGetters };
      let unorderedWarnings = [];
      _getUstensilWarnings(store, unorderedWarnings, recipe);
      _getTasteWarnings(store, unorderedWarnings, recipe);
      _getDislikedRecipeWarnings(store, unorderedWarnings, recipe);
      _getDietExclusionWarnings(store, unorderedWarnings, recipe);
      _getUserSettingWarnings(store, unorderedWarnings, recipe);
      return unorderedWarnings.sort((w1, w2) => w2.level - w1.level);
    },
  },
  mutations: {},
  actions: {
    init({ state, dispatch, rootGetters }, tastes) {
      const user = rootGetters["user/get"];
      state.userUstensils = user.ustensils;
      // Passing tastes in argument prevents a circular dependency: opTaste.add/del() -> opRecipeFilter.resetWarnings()
      state.userTastes = tastes;
      // Reset warnings cache
      state.warningsById = {};
      dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.recipeFilter.dislikedRecipes,
          apiQuery: API.profile.getDislikedRecipes,
          queryArg: [user.id, user.mainProfileId],
        },
        { root: true }
      );

      dispatch(
        "system/updateAttr",
        {
          getAttribute: (rootState) => rootState.recipeFilter.userSettings,
          apiQuery: API.userHabits.getBudgetProteins,
          queryArg: [user.id],
        },
        { root: true }
      );
    },
    computeRecipeWarnings({ dispatch }, { recipeId }) {
      if (!recipeId) {
        console.log("error: no warnings for null recipeId");
        return;
      }
      // Load recipe if it not loaded already to make getWarnings work
      dispatch("recipe/getRecipe", { recipeId }, { root: true });
    },
  },
};
