import { isFunction, partition, isPlainObject, isEmpty, isArray } from "lodash";
import axios from "axios";
import { applyAuthTokenInterceptor } from "axios-jwt";
import { setupCache } from "axios-cache-adapter";
import applyCaseMiddleware from "axios-case-converter";
import store from "@/store/index.js";
import router from "@/router/index.js";
import { API_HOST } from "@/config.js";

export function generateCancelToken() {
  const source = axios.CancelToken.source();
  const abort = () => source.cancel();
  return [source.token, abort];
}

// URL for the public API
const API_URL = API_HOST;

function logAPIError(error) {
  if (process.env.NODE_ENV != "development") return;
  console.error(`Request to ${error.config && error.config.url} failed`);
  if (error.response) {
    console.log(`    Status code: ${error.response.status}`);
    console.log("    Response:", error.response.data);
    console.log("    Response headers:", error.response.headers);
  } else if (error.request) {
    console.log("    Request:", error.request);
  } else {
    console.log("    Error:", error.message);
  }
  console.log("    Request:", error.config);
}

// Don't cache by default.
// cacheOptions needs to be passed explicitely to enable caching
const cache = setupCache({ maxAge: 0 });
const cacheOptions = { cache: { maxAge: 15 * 60 * 1000 } }; // 15mn

const client = applyCaseMiddleware(
  axios.create({
    baseURL: API_URL,
    // xsrfCookieName: "csrftoken",
    // xsrfHeaderName: "X-CSRFToken",
    // The following line needs to be uncommented if
    // frontend and backend are put on 2 differents servers
    // withCredentials: true,
    adapter: cache.adapter,
  })
);
client.interceptors.request.use(
  (config) => config,
  (error) => {
    logAPIError(error);
    return Promise.reject(error);
  }
);

////////////////////////
// JWT configuration
/////////////////////////

// Define token refresh function.
const requestRefresh = async (refresh) => {
  // Notice that this is the global axios instance, not the axiosInstance!  <-- important
  const response = await axios.post(API_URL + `/token/refresh`, { refresh });
  return response.data.access;
};

// Apply interceptor
applyAuthTokenInterceptor(client, { requestRefresh });

/// End JWT configuration

const EXPIRED_REASON_STR = "Informations d'authentification non fournies.";

client.interceptors.response.use(
  (response) => {
    if (response.data.status === "error" && response.data.error === "requires_premium") {
      // PERMISSION DENIED
      store.commit("dialog/showPremiumModal");
    }
    return response;
  },
  (error) => {
    const currentRoute = router.currentRoute.value;
    if (!axios.isCancel(error) && (!error.response || error.response.status === 503)) {
      // !error.response happens when there is a net::ERR_CONNECTION_RESET
      // MAINTENANCE
      store.commit("dialog/showMaintenanceModal");
    } else if (Math.floor(error.response.status / 100) == 5 || error.response.status == 400) {
      // ERROR
      router.push({ name: "CriticalError" });
    } else if (error.response.status === 301) {
      // PERMANENT REDIRECTION
      console.warn("WARNING : got a 301 - permanent direction - return code");
    } else if (error.response.status == 401) {
      // LOGIN REQUIRED
      store.commit("system/setLoginRedirectPage", currentRoute);
      router.push({ name: "SignIn", params: { reason: "required" } });
    } else if (error.response.status == 403) {
      // PERMISSION DENIED
      if (error.response.data.detail == EXPIRED_REASON_STR) {
        // In fact it's a LOGIN REQUIRED
        // Destroy session to prevent infinite loop (anywhere [expired] --> login [already logged] --> userhome [expired] --> login [already logged] --> ...)
        store.commit("user/logout");
        store.commit("system/setLoginRedirectPage", currentRoute);
        router.push({ name: "SignIn", params: { reason: "expired" } });
      } else {
        router.push({ name: "PermissionDenied" });
      }
    }
    logAPIError(error);
    return Promise.reject(error);
  }
);

function endpoint(urlFn, method = "get", defaultParams = {}, returnOriginalResponse = false, options = {}) {
  return async function (...args) {
    const [otherParams, urlParams] = partition(args, isPlainObject);
    const payload = otherParams[0];

    let cancelToken;
    if (otherParams.length > 1) {
      cancelToken = otherParams[1].cancelToken;
    }

    let url;
    if (isFunction(urlFn)) {
      url = urlFn(...urlParams);
    } else {
      url = urlFn;
    }

    let data;
    if (method != "get") {
      data = { ...defaultParams, ...payload };
    } else if (!isEmpty(payload)) {
      let queryParams = [];
      for (let key of Object.keys(payload)) {
        if (!isArray(payload[key])) {
          queryParams.push(`${key}=${payload[key]}`);
        } else {
          for (let item of payload[key]) {
            queryParams.push(`${key}=${item}`);
          }
        }
      }
      const queryString = queryParams.join("&");
      url = `${url}?${queryString}`;
    }

    const response = await client({
      method,
      url,
      data,
      cancelToken,
      ...options,
    });

    if (returnOriginalResponse) return response;
    else return response.data;
  };
}

export default {
  init: endpoint("/init/"),
  login: endpoint("/token/", "post", { app: "public" }, true),
  facebook_login: endpoint("/facebook-login/", "post", { app: "public" }, true),
  autologin: endpoint("/autologin/", "post", {}, true),
  signup: endpoint("/signup/", "post", { app: "public" }, true),
  facebook_signup: endpoint("/facebook-signup/", "post", { app: "public" }, true),
  resetPassword: endpoint("/reset_password/", "post", { app: "public" }),
  forgotPassword: endpoint("/forgot_password/", "post", { app: "public" }),
  validateInvite: endpoint("/biodymanager/validate_invite/", "post"),
  currentUser: endpoint("/current_user/"),
  taste: {
    save: endpoint(`/taste`, "post"),
    remove: endpoint((tasteId) => `/taste/${tasteId}`, "delete"),
  },
  user: {
    nutrientPacks: endpoint((userId) => `/user/${userId}/nutrient_packs`),
    planificationStatus: endpoint((userId) => `/user/${userId}/planification_status`),
    questionQuota: endpoint((userId) => `/user/${userId}/question_quota`),
    stats: endpoint((userId) => `/user/${userId}/stats`),
    changeSettings: endpoint((userId) => `/user/${userId}/change_settings`, "put"),
    changePassword: endpoint((userId) => `/user/${userId}/change_password`, "put"),
    emailOptions: endpoint((userId) => `/user/${userId}/email_options`),
    addUstensil: endpoint((userId) => `/user/${userId}/add_ustensil`, "post"),
    removeUstensil: endpoint((userId) => `/user/${userId}/remove_ustensil`, "post"),
    preconfigure: endpoint((userId) => `/user/${userId}/preconfigure`, "post"),
    setEmailOptions: endpoint((userId) => `/user/${userId}/set_email_options`, "post"),
    enableNutrientPack: endpoint((userId) => `/user/${userId}/enable_nutrient_pack`, "post"),
    subscribeToDiet: endpoint((userId, dietId) => `/user/${userId}/subscribe_to_diet/${dietId}`, "post"),
    diagnose: endpoint((userId, dietId) => `/user/${userId}/diagnose/${dietId}`, "post"),
  },
  userDay: {
    get: endpoint((userId, date) => `/user/${userId}/day_to_fill/${date}`),
    indicators: endpoint((userId, date) => `/user/${userId}/day/${date}/indicators`),
    structure: endpoint((userId, date) => `/user/${userId}/day/${date}/structure`),
    suggest: endpoint((userId, date) => `/user/${userId}/suggest/${date}`, "post"),
    setDishrecipe: endpoint((userId, dishId) => `/user/${userId}/set_dishrecipe/${dishId}`, "post"),
    notNow: endpoint((userId, recipeId) => `/user/${userId}/not_now/${recipeId}`, "post"),
    improve: endpoint((userId, date) => `/user/${userId}/day/${date}/improve`, "post"),
    clearDish: endpoint((userId, dishId) => `/user/${userId}/clear_dish/${dishId}`, "post"),
    deleteDish: endpoint((userId, dishId) => `/user/${userId}/delete_dish/${dishId}`, "post"),
    addDish: endpoint((userId, mealSlotId) => `/user/${userId}/add_dish/${mealSlotId}`, "post"),
    forceAsFilled: endpoint((userId, date) => `/user/${userId}/day/${date}/force_as_filled`, "post"),
    validateDish: endpoint((userId, dishId) => `/user/${userId}/validate_dish/${dishId}`, "post"),
    setMealPlace: endpoint((userId, date) => `/user/${userId}/day/${date}/set_meal_place`, "post"),
    toggleDishActivation: endpoint((userId, dishId) => `/user/${userId}/toggle_dish_activation/${dishId}`, "post"),
    toggleDishrecipeShopping: endpoint(
      (userId, dishId) => `/user/${userId}/toggle_dishrecipe_shopping/${dishId}`,
      "post"
    ),
  },
  userDays: {
    get: endpoint((userId, day) => `/user/${userId}/menu/${day}`),
    daysStates: endpoint((userId) => `/user/${userId}/days_states`),
  },
  profiles: endpoint((userId) => `/user/${userId}/profile`),
  profile: {
    update: endpoint((userId, profileId) => `/user/${userId}/profile/${profileId}`, "put"),
    save: endpoint((userId) => `/user/${userId}/profile`, "post"),
    remove: endpoint((userId, profileId) => `/user/${userId}/profile/${profileId}`, "delete"),
    nbDislikes: endpoint((userId, profileId) => `/user/${userId}/profile/${profileId}/nb_dislikes`),
    getDislikedRecipes: endpoint((userId, profileId) => `/user/${userId}/profile/${profileId}/get_disliked_recipes`),
    metricHistory: endpoint((userId, profileId) => `/user/${userId}/profile/${profileId}/metric_history`),
    dislikeRecipe: endpoint((userId, profileId) => `/user/${userId}/profile/${profileId}/dislike_recipe`, "post"),
    updateMetrics: endpoint((userId, profileId) => `/user/${userId}/profile/${profileId}/update_metrics`, "post"),
  },
  profileAttendance: {
    get: endpoint((profileId) => `/profile/${profileId}/attendance`),
    update: endpoint((profileId) => `/profile/${profileId}/attendance`, "put"),
  },
  userHabits: {
    get: endpoint((userId) => `/user/${userId}/meal_types_habits`),
    mealTypeHabits: endpoint((userId, mealTypeId) => `/user/${userId}/meal_type/${mealTypeId}/habits`),
    getBudgetProteins: endpoint((userId) => `/user/${userId}/budget_proteins`),
    setBudgetProteins: endpoint((userId) => `/user/${userId}/set_budget_proteins`, "post"),
    enableMealDish: endpoint(
      (userId, mealTypeId) => `/user/${userId}/meal_type/${mealTypeId}/enable_meal_dish`,
      "post"
    ),
    disableMealDish: endpoint(
      (userId, mealTypeId) => `/user/${userId}/meal_type/${mealTypeId}/disable_meal_dish`,
      "post"
    ),
    forceRecipe: endpoint((userId, mealTypeId) => `/user/${userId}/meal_type/${mealTypeId}/force_recipe`, "post"),
    setMealSpeed: endpoint((userId, mealTypeId) => `/user/${userId}/meal_type/${mealTypeId}/set_meal_speed`, "post"),
    setSuggest: endpoint((userId, mealTypeId) => `/user/${userId}/meal_type/${mealTypeId}/set_suggest`, "post"),
  },
  rawStates: endpoint("/raw_state"),
  restrictedFoods: endpoint((profileId) => `/restricted_food?profile_id=${profileId}`),
  configStage: endpoint((userId) => `/config_stage?user_id=${userId}`),
  completeStage: endpoint((userId) => `/user/${userId}/config_stages/complete`, "post"),
  activateFreeTrial: endpoint((user) => `/user/${user}/activate_free_trial`, "post"),
  tastes: endpoint((profileId, nested) => `/taste?profile_id=${profileId}&nested=${nested}`),
  diets: endpoint("/diet"),
  diet: {
    excludedFoodtags: endpoint((dietId) => `/diet/${dietId}/excluded_foodtags`),
    forewarnedFoodtags: endpoint((dietId) => `/diet/${dietId}/forewarned_foodtags`),
  },
  eaters: endpoint((userId) => `/user/${userId}/eater`),
  food: {
    availableOptions: endpoint((foodId) => `/food/${foodId}/available_options`),
  },
  foodConversion: {
    searchByFood: endpoint((foodId) => `/food_conversion?food_id=${foodId}`),
  },
  foodTags: endpoint("food_tag"),
  foodSearch: endpoint((keyword) => `/food/search/${encodeURIComponent(keyword)}`, "get", {}, false, {
    ...cacheOptions,
  }),
  foodTagSearch: endpoint((keyword) => `/food_tag/search/${encodeURIComponent(keyword)}`, "get", {}, false, {
    ...cacheOptions,
  }),
  recipeSearch: endpoint((keyword) => `/recipe/search/${encodeURIComponent(keyword)}`),
  recipeImgUpload: endpoint((recipeId) => `/recipe/${recipeId}/upload_img`, "post"),
  tariffs: endpoint("/tariffs/"),
  ustensils: endpoint("/ustensil"),
  ustensilCategories: endpoint("/ustensil_category"),
  shoppingList: {
    get: endpoint((userId, shoppingListId) => `/user/${userId}/shopping_list/${shoppingListId}`),
    flyMenuItems: endpoint(
      (userId, shoppingListId) => `/user/${userId}/shopping_list/${shoppingListId}/fly_menu_items`
    ),
    availableDays: endpoint((userId) => `/user/${userId}/shopping_list/available_days`),
    history: endpoint((userId) => `/user/${userId}/shopping_list/history`),
    buildNew: endpoint((userId) => `/user/${userId}/shopping_list/build_new`, "post"),
    toggleItem: endpoint((userId, itemId) => `/user/${userId}/shopping_list/toggle_item/${itemId}`, "post"),
    sendByMail: endpoint(
      (userId, shoppingListId) => `/user/${userId}/shopping_list/${shoppingListId}/send_by_mail`,
      "post"
    ),
    remove: endpoint((userId, shoppingListId) => `/user/${userId}/shopping_list/${shoppingListId}/delete`, "post"),
  },
  shoppingItem: {
    save: endpoint("/shopping_item", "post"),
    remove: endpoint((shoppingItemId) => `/shopping_item/${shoppingItemId}`, "delete"),
    force: endpoint((shoppingItemId) => `/shopping_item/${shoppingItemId}/force`, "put"),
  },
  discussion: {
    get: endpoint((discussionId) => `/discussion/${discussionId}`),
    save: endpoint(`/discussion`, "post"),
    read: endpoint((discussionId) => `/discussion/${discussionId}/read`, "post"),
  },
  message: {
    get: endpoint((messageId) => `/message/${messageId}`),
    update: endpoint((messageId) => `/message/${messageId}`, "put"),
    save: endpoint(`/message`, "post"),
  },
  cookbookRecipes: endpoint((userId) => `/user/${userId}/cookbook_recipe`),
  cookbookRecipe: {
    save: endpoint((userId) => `/user/${userId}/cookbook_recipe`, "post"),
    deleteByRecipeId: endpoint((userId) => `/user/${userId}/cookbook_recipe/delete_by_recipe_id`, "post"),
  },
  cookingMethod: {
    food: endpoint((foodId) => `/cooking_method/food/${foodId}`),
  },
  recipes: endpoint("/recipe"),
  recipe: {
    get: endpoint((recipeId) => `/recipe/${recipeId}`),
    update: endpoint((recipeId) => `/recipe/${recipeId}`, "put"),
    getMany: endpoint("/recipe/get_many"),
    fromKey: endpoint((key) => `/recipe/from_key/${key}`),
    getSuggestedFoodTags: endpoint((recipeId) => `/recipe/${recipeId}/get_suggested_food_tags`),
    save: endpoint("/recipe", "post"),
    remove: endpoint((recipeId) => `/recipe/${recipeId}`, "delete"),
    personalRecipes: endpoint((userId) => `/user/${userId}/personal_recipes?ids_only=true`),
    withIngredients: endpoint((recipeId) => `/recipe/${recipeId}/with_ingredients`),
    nutrients: endpoint((recipeId) => `/recipe/${recipeId}/nutrients`),
    ratings: endpoint((recipeId) => `/recipe/${recipeId}/ratings`),
    userRating: endpoint((recipeId) => `/recipe/${recipeId}/user_rating`),
    randomSeasonSelection: endpoint("/recipe/random_season_selection", "get", {}, false, {
      ...cacheOptions,
    }),
    rate: endpoint((recipeId) => `/recipe/${recipeId}/rate`, "post"),
    addUstensil: endpoint((recipeId) => `/recipe/${recipeId}/add_ustensil`, "post"),
    removeUstensil: endpoint((recipeId) => `/recipe/${recipeId}/remove_ustensil`, "post"),
    addTag: endpoint((recipeId) => `/recipe/${recipeId}/add_tag`, "post"),
    removeTag: endpoint((recipeId) => `/recipe/${recipeId}/remove_tag`, "post"),
    addDishType: endpoint((recipeId) => `/recipe/${recipeId}/add_dish_type`, "post"),
    removeDishType: endpoint((recipeId) => `/recipe/${recipeId}/remove_dish_type`, "post"),
  },
  recipeInstruction: {
    save: endpoint("/recipe_instruction", "post"),
    update: endpoint((recipeInstructionId) => `/recipe_instruction/${recipeInstructionId}`, "put"),
    remove: endpoint((recipeInstructionId) => `/recipe_instruction/${recipeInstructionId}`, "delete"),
  },
  recipeTags: endpoint("/recipe_tag"),
  dishTypes: endpoint("/dish_type"),
  dishType: {
    fromMealType: endpoint((mealTypeId) => `/dish_type/from_meal_type/${mealTypeId}`),
  },
  ingredient: {
    save: endpoint("/ingredient", "post"),
    update: endpoint((ingredientId) => `/ingredient/${ingredientId}`, "put"),
    remove: endpoint((ingredientId) => `/ingredient/${ingredientId}`, "delete"),
  },
  mealPlaces: endpoint("/meal_place"),
  locations: endpoint("/location?tree=1"),
  nutrients: endpoint("/nutrient"),
  nutrientCategories: endpoint("/nutrient_categories"),
  discussions: endpoint("/discussion"),
  mealSharing: {
    get: endpoint((planning) => `/planning/${planning}/attendance`),
    update: endpoint((planning) => `/planning/${planning}/attendance`, "put"),
  },
  mealSlot: {
    externalSuggest: endpoint((mealSlotId) => `/meal_slot/${mealSlotId}/external_suggest`),
    setSpeed: endpoint((mealSlotId) => `/meal_slot/${mealSlotId}/set_speed`, "post"),
    addEater: endpoint((mealSlotId) => `/meal_slot/${mealSlotId}/add_eater`, "post"),
    removeEater: endpoint((mealSlotId) => `/meal_slot/${mealSlotId}/remove_eater`, "post"),
  },
};
