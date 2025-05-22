import { createStore } from "vuex";
import analytics from "./analytics.js";
import cache from "./cache.js";
import cookbook from "./cookbook.js";
import configStage from "./configStage.js";
import dialog from "./dialog.js";
import diet from "./diet.js";
import discussion from "./discussion.js";
import equipment from "./equipment.js";
import meta from "./meta.js";
import planning from "./planning.js";
import profile from "./profile.js";
import recipe from "./recipe.js";
import recipeFilter from "./recipeFilter.js";
import shopping from "./shopping.js";
import system from "./system.js";
import services from "./services.js";
import taste from "./taste.js";
import user from "./user.js";

export default createStore({
  modules: {
    analytics,
    cache,
    cookbook,
    configStage,
    dialog,
    diet,
    discussion,
    equipment,
    meta,
    planning,
    profile,
    recipe,
    recipeFilter,
    shopping,
    system,
    services,
    taste,
    user,
  },
});
