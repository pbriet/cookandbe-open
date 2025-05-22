<template>
  <!-- Need reinit after configuration change popup  -->
  <Dialog
    id="configuration-changed-popup"
    :open="showConfigurationChangePopup"
    :onClose="ignoreConfigurationChange"
    :closeBtn="true"
  >
    <div class="dialog-title">
      <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
      Attention
    </div>
    <div class="dialog-body">
      <h3>Confirmez-vous la réinitialisation ?</h3>
      <ul>
        <li>Les suggestions pour ce jour et les suivants seront perdues.</li>
        <li v-if="nbShoppingListsAfterDate > 1">
          <b>{{ nbShoppingListsAfterDate }}</b> listes de courses seront supprimées.
        </li>
        <li v-if="nbShoppingListsAfterDate == 1"><b>1</b> liste de courses sera supprimée.</li>
      </ul>
      <div class="col-12 op-vs">
        <div class="col-6 col-sm-4 fright">
          <button class="col-12 btn btn-secondary" @click="ignoreConfigurationChange">Annuler</button>
        </div>
        <div class="col-6 col-sm-4 fright">
          <button class="col-12 btn btn-success" @click="reinitFromMeta(true)">Mettre à jour</button>
        </div>
      </div>
    </div>
  </Dialog>

  <!-- Add/remove/change mealPlaces  -->
  <Dialog id="meal-place-editor-popup" :open="showMealplaceEditorPopup" :onClose="hideMealplaceEditor" :closeBtn="true">
    <DayMealPlaceEditor
      :date="date"
      v-if="dayContent"
      :onValidate="hideMealplaceEditor"
      v-model:mealPlaceEdition="mealPlaceEdition"
    />
  </Dialog>

  <!-- Why calories popup -->
  <Dialog id="why-calories" :open="showWhyCalories" :onClose="hideWhyCaloriesPopup" :closeBtn="true">
    <div class="dialog-title">Comment sont déterminées mes calories ?</div>
    <div class="dialog-body">
      <div class="op-raw-table">
        <div>
          <FontAwesomeIcon :icon="['fas', 'user']" class="me-3" />
          <span
            >Vos apports caloriques sont calculés à partir de votre <b>profil</b> (âge, taille, poids, sexe, activité
            physique).</span
          >
        </div>
        <div>
          <FontAwesomeIcon :icon="['fas', 'wrench']" />
          <span>Mais également selon le mode d'alimentation que vous avez choisi.</span>
        </div>
      </div>
    </div>
  </Dialog>

  <!-- DishRecipe details popup -->
  <Dialog
    id="recipe-selection-dialog"
    :open="showRecipeSelection"
    :closeBtn="true"
    :onClose="unselectRecipe"
    :noFade="true"
  >
    <div class="dialog-title">
      <span v-if="current.state !== 'dislike'">{{ getFullDishCaption() }}</span>
      <span v-if="current.state === 'dislike' && selection">"{{ selection.recipe.name }}"</span>
    </div>
    <div class="dialog-body">
      <PleaseWait :until="current.state !== 'please_wait'" caption="Veuillez patienter">
        <div class="row">
          <div class="col-12 col-md-8">
            <SelectionBlock
              :dishTypes="dishTypes"
              :onNotNow="onNotNow"
              :selection="selection"
              :current="current"
              :dayStatus="dayStatus"
              :onDislike="onDislike"
              :onDislikeFinished="onDislikeFinished"
              :onLockRecipe="onLockRecipe"
              :showReplacePopup="showReplacePopup"
              :deleteDish="deleteDish"
              v-if="selection"
            />
          </div>
          <div class="recipe-stats d-none d-md-block col-md-4">
            <!-- Recipe stats panel -->
            <RecipeStats
              v-if="selection?.recipe && mainProfile"
              :recipe="selection.recipe"
              :ratio="dayContent.ratios[selection.dish.id][mainProfile.id]"
              :width="250"
            />
            <div v-if="dayContent && selection && dictLen(dayContent.ratios[selection.dish.id]) > 1" class="op-vs">
              <h4>Qui mange quoi ?</h4>
              <RatioPieChart width="100%" :ratios="dayContent.ratios[selection.dish.id]" />
            </div>
          </div>
          <div class="col-12 col-md-8">
            <div class="btn btn-success fright" @click="unselectRecipe">Fermer</div>
          </div>
        </div>
      </PleaseWait>
    </div>
  </Dialog>

  <ReplaceRecipeDialog
    :open="showReplaceRecipePopup"
    :hideReplacePopup="hideReplacePopup"
    :search="search"
    @update:search="search = $event"
    :onChangeRecipe="onChangeRecipe"
    :onAddRecipe="onAddRecipe"
  />

  <div id="please-wait-global" v-if="current.state === 'please_wait'">
    <PleaseWait />
  </div>

  <div id="op-day-planner-page" class="op-page">
    <div class="op-page-title">
      <h1>Mes repas</h1>
    </div>

    <!-- Day review content -->
    <div class="day-planner-page-content container-fluid">
      <DaySelector baseUrl="DayPlanner" baseUrlToday="DayPlanner" baseUrlPast="DayView" :currentDate="date" />
      <div v-if="tooMuchInFuture" id="too-much-in-future">
        <span class="op-icon-dxxxl">
          <FontAwesomeIcon :icon="['fas', 'ban']" />
        </span>
        <span class="op-font-xl">
          Désolé, il n'est pas possible de planifier au-delà de {{ tooMuchInFuture.maxDays }} jours dans le futur.<br />
          Merci de revenir plus tard.
        </span>
      </div>

      <div class="day-planner-day-panel row" v-if="!tooMuchInFuture">
        <!-- Planning panel -->
        <div class="col-12 col-md-9 day-planner-left-panel">
          <DayPlannerHeader
            :dayStatus="dayStatus"
            :date="date"
            :onSkipDay="skipDay"
            :onMoveToNextDay="moveToNextDay"
            :onModifyMeals="showMealplaceEditor"
            :updateFromMeta="showConfigurationChange"
          />
          <div>
            <div class="alert alert-danger" v-if="disabledFilters.length > 0 && !dayStatus.shoppingListId">
              <FontAwesomeIcon :icon="['fas', 'exclamation-circle']" />
              Désolé, aucune recette ne correspond à vos contraintes. Nous avons désactivé les contraintes suivantes
              dans la suggestion ci-dessous:
              <ul>
                <li v-for="disabledFilter in disabledFilters" :key="disabledFilter.dishId">
                  <FontAwesomeIcon :icon="['fas', 'times']" />
                  <span v-for="(disFilter, index) in disabledFilter.filters" :key="disFilter">
                    {{ disFilter }} <span v-if="index != disabledFilter.filters.length - 1">, </span>
                  </span>
                  ({{ getFullDishCaption(disabledFilter.dishId) }})
                </li>
              </ul>
            </div>

            <DayIndicators
              :indicators="indicators"
              v-if="indicators && dayStatus.validated"
              mode="small-screen"
              :currentDate="date"
              classes="d-md-none"
              :showWhyCalories="showWhyCaloriesPopup"
            />

            <div class="clearfix"></div>
            <DayMosaic
              v-if="dayStatus && dayStatus.validated"
              :date="date"
              :selection="selection"
              :dayContent="dayContent"
              :onSelectDish="selectDish"
              :selectedDishId="selection?.dish.id"
              :dishTypesById="dishTypes"
              :onNewDish="onNewDish"
              :onNotNow="onNotNow"
              :onModifyMealPlace="showMealplaceEditor"
              :onChangeMealSpeed="onChangeSpeed"
              :onChangeMealEaters="onChangeEaters"
              :preventEdition="dayStatus.shoppingListId"
            />
          </div>
          <!-- Planning panel -->
        </div>

        <!-- Day indicators panel -->
        <div class="col-12 col-md-3 d-none d-md-block">
          <DayIndicators
            :indicators="indicators"
            v-if="indicators && dayStatus.validated"
            mode="large-screen"
            :currentDate="date"
            :showWhyCalories="showWhyCaloriesPopup"
          />
        </div>
        <!-- Indicators panel -->
      </div>
      <!-- Day panel -->
    </div>
    <!-- Day review content -->
  </div>
  <!-- Day review page -->
</template>

<script>
import API from "@/api.js";
import { mapGetters, mapMutations } from "vuex";
import { find, extend, upperFirst, size } from "lodash";
import { DateTime } from "luxon";
import { isPast, tomorrow, stringToDate, nextDay } from "@/common/dates.js";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import Dialog from "@/components/interface/Dialog.vue";
import RatioPieChart from "@/components/user/RatioPieChart.vue";
import DaySelector from "@/components/planning/DaySelector.vue";
import DayMealPlaceEditor from "@/components/planning/DayMealPlaceEditor.vue";
import DayPlannerHeader from "@/components/planning/DayPlannerHeader.vue";
import ReplaceRecipeDialog from "@/components/planning/ReplaceRecipeDialog.vue";
import SelectionBlock from "@/components/planning/SelectionBlock.vue";
import DayIndicators from "@/components/planning/DayIndicators.vue";
import DayMosaic from "@/components/planning/DayMosaic.vue";
import RecipeStats from "@/components/recipe/RecipeStats.vue";

/*
 * Component for displaying profiles related to current user
 */
export default {
  name: "DayPlanner",
  props: [],
  data: () => ({
    showConfigurationChangePopup: false,
    showRecipeSelection: false,
    showMealplaceEditorPopup: false,
    showReplaceRecipePopup: false,
    mealPlaceEdition: {}, // Used to retrieve some values when hiding the popup
    search: { keyword: "", limit: 5, mode: "all", recipes: [] },
    current: {}, // Current state
    selection: null, // This is the dish we're currently focusing on
    keyword: "", // keyword is the keyword used for search
    indicators: null, // Nutrient indicators
    dayContent: null, // Content / structure of current day
    mealSlotById: {},
    dishById: {},
    tooMuchInFuture: null,
    disabledFilters: [],
    dayStatus: null,
  }),
  mounted() {
    this.init(this.date);
  },
  beforeRouteUpdate(to, _, next) {
    // Called when $route.params.day changes
    this.init(this.dateFromRouteParam(to.params.day));
    next();
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
      showWhyCalories: "dialog/whyCalories",
      mainProfile: "profile/getMainProfile",
      dishTypes: "cache/getDishTypesDict",
    }),
    date() {
      return this.dateFromRouteParam(this.$route.params.day);
    },
    nbShoppingListsAfterDate() {
      return this.$store.getters["shopping/nbShoppingListsAfterDate"](this.date);
    },
  },
  methods: {
    dictLen: size,
    ...mapMutations({
      hideWhyCaloriesPopup: "dialog/hideWhyCalories",
      showWhyCaloriesPopup: "dialog/showWhyCalories",
      metaSetTitle: "meta/setTitle",
    }),
    dateFromRouteParam(param) {
      if (!param) {
        return tomorrow();
      }
      return stringToDate(param);
    },
    init(date) {
      this.initSearch();
      if (isPast(date)) {
        // Date is in past -> redirect to classic day view
        this.$router.push({ name: "DayView", params: { day: date.toDateString() } });
        return;
      }
      this.metaSetTitle(upperFirst(DateTime.fromJSDate(date).setLocale("fr").toFormat("EEEE dd MMMM")));

      this.keyword = "";
      this.indicators = null;
      this.dayContent = null;
      this.dayStatus = null;
      this.current = {};
      this.mealPlaceEdition = {};
      this.mealSlotById = {};
      this.dishById = {};
      this.tooMuchInFuture = null;
      this.disabledFilters = [];
      this.clearSelection();

      this.reset(
        date,
        { init: true },
        () => {
          this.$store.dispatch("shopping/update");
        },
        false
      );
    },
    initSearch() {
      this.search = { keyword: "", limit: 5, mode: "all", recipes: [] };
      this.resetSearch();
    },
    clearSelection() {
      this.selection = null;
    },
    getFullDishCaption(dishId) {
      if (!this.dishTypes || !this.dayContent || (!this.selection && !dishId)) {
        return "";
      }
      let dish;
      if (dishId) {
        dish = this.dishById[dishId];
      } else {
        dish = this.selection.dish;
      }
      if (!dish) {
        return "";
      }
      const mealslot = this.getMealslotFromDish(dish);
      const suggestion = find(this.dayContent.content, { mealSlot: { id: dish.mealId } });
      if (!suggestion) {
        return "";
      }
      const mealName = mealslot.mealSlot.mealType.name;
      const dishName = this.dishTypes[dish.mainDishTypeId].name;
      return mealName + " - " + dishName;
    },
    /*
     * Reload content and indicators
     */
    reset(date, refreshArgs, callbackFcn, keepSelection, callbackAfterReloadContent) {
      this.current.state = "please_wait";
      if (!keepSelection) {
        this.clearSelection();
      }
      this.optimizeMenu(date, refreshArgs, () => {
        this.reloadContent(date, () => {
          if (this.selection && keepSelection) {
            this.updateSelection(this.selection.dish.id, this.selection.recipeIndex);
          }
          callbackAfterReloadContent && callbackAfterReloadContent();
        });
        this.reloadIndicators(date);
        callbackFcn && callbackFcn();
      });
    },
    async reloadIndicators(date) {
      const data = await API.userDay.indicators(this.userId, date.toDateString());
      this.indicators = data.content;
      this.updateStateToSuggestOrComplete();
    },
    async reloadContent(date, callback, mealId) {
      const data = await API.userDay.get(this.userId, date.toDateString());
      this.resetModifiedDishes();
      if (mealId) {
        this.updateMealOnly(data, mealId);
      } else {
        // Refreshing everything
        this.setModifiedDay(data, this.dayContent);
        this.dayContent = data;
      }
      this.onLoadedDayContent();
      callback && callback();
    },
    /*
     * Function that updates this.dayContent, but only on a given mealId
     */
    updateMealOnly(data, mealId) {
      // Only refreshing a given meal  //  UGLY
      for (let j = 0; j < this.dayContent.content.length; j++) {
        if (this.dayContent.content[j].mealSlot.id == mealId) {
          for (let i = 0; i < data.content.length; i++) {
            if (data.content[i].mealSlot.id == mealId) {
              this.setModifiedMeal(data.content[i], this.dayContent.content[j]);
              extend(this.dayContent.content[j], data.content[i]);
              break;
            }
          }
          break;
        }
      }
    },
    setModifiedDish(newDish, oldDish) {
      let nbModified = 0;
      if (!oldDish) {
        return nbModified;
      }
      if (this.selection && newDish.id === this.selection.dish.id) {
        // Special case : we do not want the currently selected dish to be set as "modified"
        for (const recipe of newDish.recipes) {
          recipe.modified = false;
        }
        return nbModified;
      }
      for (const newRecipe of newDish.recipes) {
        const oldRecipe = find(oldDish.recipes, ["id", newRecipe.id]);
        if (!oldRecipe && !newRecipe.validated) {
          newRecipe.modified = true;
          nbModified += 1;
        }
      }
      return nbModified;
    },
    /*
     * Set all dishes as being not modified
     */
    resetModifiedDishes() {
      if (!this.dayContent) {
        return;
      }
      for (const meal of this.dayContent.content) {
        if (!meal.dishes) {
          continue;
        }
        for (const dish of meal.dishes) {
          for (const recipe of dish.recipes) {
            recipe.modified = false;
          }
        }
      }
    },
    /*
     * From a dish, returns the mealslot
     */
    getMealslotFromDish(dish) {
      for (const meal of this.dayContent.content) {
        if (meal.mealSlot.id === dish.mealId) {
          return meal;
        }
      }
    },
    setModifiedMeal(newMeal, oldMeal) {
      let nb = 0;
      if (!oldMeal || !newMeal.dishes) {
        return nb;
      }
      for (const newDish of newMeal.dishes) {
        const oldDish = find(oldMeal.dishes, ["id", newDish.id]);
        nb += this.setModifiedDish(newDish, oldDish);
      }
      return nb;
    },
    setModifiedDay(newDay, oldDay) {
      let nb = 0;
      if (!oldDay) {
        return nb;
      }
      for (const newMeal of newDay.content) {
        const oldMeal = find(oldDay.content, { mealSlot: { id: newMeal.mealSlot.id } });
        nb += this.setModifiedMeal(newMeal, oldMeal);
      }
      return nb;
    },
    /*
     * Go the next day
     */
    moveToNextDay() {
      this.$router.push({ name: "DayPlanner", params: { day: nextDay(this.date).toDateString() } });
    },
    skipDay(value) {
      this.forceDayAsFilled(!value);
    },
    /*
     * Set the day as being filled
     * If checkMetaplanningUpdate is True, returns a promise saying if
     * metaplanning update is required and can be done automatically
     */
    forceDayAsFilled(value) {
      // If value is false, this day is considered as skipped
      API.userDay
        .forceAsFilled(this.userId, this.date.toDateString(), {
          value: value,
        })
        .then(() => {
          this.$store.dispatch("shopping/update");
        });
      this.dayStatus.skipped = !value;
      this.dayStatus.validated = value;
      if (value) {
        this.dayStatus.nbPlannedDays += 1;
      } else {
        this.dayStatus.nbPlannedDays -= 1;
      }
    },
    /*
     * Optimize the day content server-side. Display the first one
     */
    async optimizeMenu(date, args, callback) {
      // Default values for arguments  -- JS is so pretty :'(
      args.init = typeof args.init === "undefined" ? false : args.init;
      args.recalculate = typeof args.recalculate === "undefined" ? false : args.recalculate;
      args.reinit = typeof args.resetFromMetaplaning === "undefined" ? false : args.resetFromMetaplaning;
      args.restartFromExisting = typeof args.restartFromExisting === "undefined" ? true : args.restartFromExisting;
      args.minimizeChange = typeof args.minimizeChange === "undefined" ? null : args.minimizeChange;

      const data = await API.userDay.suggest(this.userId, date.toDateString(), args);
      if (data.status === "too_much_in_future") {
        // Cannot plan too much in the future
        this.tooMuchInFuture = { maxDays: data.maxNbDays };
        this.current.state = "suggest";
        return;
      }
      // TODO : suggestions are nearly not used (but dayContent API instead)
      // they're only used for disabled filters...
      callback && callback();
      this.disabledFilters = [];
      for (const suggestion of data.suggestions) {
        const filters = suggestion.disabledFilters;
        if (filters && filters.length > 0) {
          const dishId = suggestion.dishId;
          this.disabledFilters.push({ dishId, filters });
        }
      }
      // Removing suggestions from data (keeping other infos on day)
      data.suggestions = null;
      this.dayStatus = data;
      // Updating service
      this.$store.dispatch("planning/update");
    },
    async loadSelectionRecipe() {
      const recipe = this.selection.dish.recipes[this.selection.recipeIndex];
      this.selection.recipe = await this.$store.dispatch("recipe/getSummary", recipe.id);
    },
    resetRecipeSelection() {
      this.selection.recipe = this.selection.recipeIndex = null;
    },
    /*
     * When the day content is loaded, index dishes by id, for dynamic update of content
     */
    onLoadedDayContent() {
      this.mealSlotById = {};
      this.dishById = {};
      for (const meal of this.dayContent.content) {
        this.mealSlotById[meal.mealSlot.id] = meal.mealSlot;
        if (meal.dishes) {
          for (const dish of meal.dishes) {
            dish.mealId = meal.mealSlot.id;
            this.dishById[dish.id] = dish;
          }
        }
      }
    },
    /*
     * The user says "not now": report it to the server, and ask for new suggestions
     */
    async onNotNow(recipe, dishId) {
      if (dishId === null) {
        dishId = this.selection.dish.id;
      }
      this.current.state = "please_wait";
      await API.userDay.notNow(this.userId, recipe.id, { dishId });
      this.recalculate();
    },
    /*
     * The user says "I don't like" : show the panel that displays the ingredients
     */
    onDislike() {
      this.current.state = "dislike";
    },
    /*
     * The user has disliked (or not) something, get back to normal
     */
    onDislikeFinished(hasDisliked) {
      if (hasDisliked) {
        this.current.state = "please_wait";
        this.resetRecipeSelection();
        // Set current dish as being not forced/not validated
        API.userDay.clearDish(this.userId, this.selection.dish.id).then(() => {
          this.recalculate();
        });
        return;
      }
      this.updateStateToSuggestOrComplete(false);
    },

    /*
     * The user has validated/locked the current dishrecipe
     */
    onLockRecipe(dish, recipe) {
      this.current.state = "please_wait";
      API.userDay
        .validateDish(this.userId, this.selection.dish.id, {
          recipeId: recipe.id,
        })
        .then((data) => {
          this.onLockedRecipe(data, dish, recipe);
        });
      this.unselectRecipe();
    },
    onLockedRecipe(data, dish, recipe) {
      if (data.hasModifiedStructure) {
        this.reloadContent(this.date, () => {
          this.updateStateToSuggestOrComplete(true);
        }); // Structure has been modified : reload
      } else {
        // Just set validate to true where it should be
        for (let i = 0; i < dish.recipes.length; i++) {
          if (dish.recipes[i].id === recipe.id) {
            dish.recipes[i].validated = true;
          }
        }
        this.updateStateToSuggestOrComplete(true);
      }
    },
    onChangeEaters(mealslot) {
      this.reloadContent(this.date, null, mealslot.mealSlot.id);
    },
    onChangeSpeed(mealslot, newValue, previousValue) {
      mealslot.mealSlot.speed = newValue;
      if (mealslot.mealSlot.speed > previousValue) {
        // There is a weaker constraint, just update day content
        this.reloadContent(this.date, null, mealslot.mealSlot.id);
      } else {
        // Needs to recalculation
        this.deepRecalculate();
      }
    },
    onNewDish() {
      this.deepRecalculate();
    },
    /*
     * change state to "suggest"
     * else to "completed"
     */
    updateStateToSuggestOrComplete(resetSelection) {
      if (resetSelection) {
        this.clearSelection();
      }
      if (this.selection) {
        this.current.state = "suggest";
        return;
      }
      this.current.state = "completed";
    },
    showMealplaceEditor() {
      this.mealPlaceEdition = {};
      this.showMealplaceEditorPopup = true;
    },
    hideMealplaceEditor() {
      this.showMealplaceEditorPopup = false;
      if (this.mealPlaceEdition.recalc) {
        this.deepRecalculate();
      } else if (this.mealPlaceEdition.reload) {
        this.reloadContent(this.date);
      }
      this.mealPlaceEdition = {}; // Resetting for safety
    },
    showReplacePopup() {
      this.showReplaceRecipePopup = true;
    },
    hideReplacePopup() {
      this.showReplaceRecipePopup = false;
    },
    /*
     * Calls the backend API to replace the current selected dish with a new one with the recipe selected to
     * replace.
     */
    async replaceDish(recipe, recipeIndex, dishId, mealId, ratio) {
      this.hideReplacePopup();
      this.current.state = "please_wait";

      const data = await API.userDay.setDishrecipe(this.userId, dishId, {
        recipeId: recipe.id,
        index: recipeIndex,
        ratio: ratio,
        validated: true,
        force: true,
        updateDishType: true,
      });
      if (data.status === "error") {
        this.updateStateToSuggestOrComplete();
        return;
      }
      this.optimizeMenu(this.date, { recalculate: true }, async (onlyMeal) => {
        if (onlyMeal) {
          this.reloadContent(this.date, this.clearSelection, mealId);
        } else {
          this.reloadContent(this.date, this.clearSelection);
        }
        await this.reloadIndicators(this.date);
        this.updateStateToSuggestOrComplete();
      });
    },
    onChangeRecipe(recipe) {
      const dishId = this.selection.dish.id;
      const mealId = this.selection.dish.mealId;
      const ratio = this.selection.ratio;
      const recipeIndex = this.selection.recipeIndex;

      this.resetSearch();

      this.replaceDish(recipe, recipeIndex, dishId, mealId, ratio);
      this.unselectRecipe();
    },
    resetSearch() {
      this.search.offset = 0;
      this.search.keyword = "";
      this.search.nbRecipes = 0;
      this.search.recipes = [];
    },
    /*
     * When a user clicks on a dish
     */
    selectDish(dishId, recipe) {
      let recipeIndex = 0;
      if (recipe) {
        if (recipe.modified) {
          recipe.modified = false;
        }
        const dish = this.dishById[dishId];
        recipeIndex = dish.recipes.indexOf(recipe);
      }
      if (this.selection && this.selection.dish.id === dishId && this.selection.recipeIndex === recipeIndex) {
        this.clearSelection();
        return;
      }
      this.resetSearch();
      this.updateSelection(dishId, recipeIndex);
      this.showRecipeSelection = true;
    },
    unselectRecipe() {
      this.clearSelection();
      this.showRecipeSelection = false;
    },
    /*
     * Removing a recipe in the dish, or the dish itself
     */
    async deleteDish(dish, recipe, recipeIndex) {
      const dishTypeId = dish.dishTypeIds[recipeIndex];
      const isComplexDishtype = dish.dishTypeIds.length > 1;
      // Removing the dish
      if (!isComplexDishtype) {
        const mealslot = this.getMealslotFromDish(dish);
        // Simple dish type, removing it directly and call the backend silently
        const iDish = mealslot.dishes.indexOf(dish);
        mealslot.dishes.splice(iDish, 1);
      }
      this.unselectRecipe();
      // Calling the API
      await API.userDay.deleteDish(this.userId, dish.id, { dishTypeId });
      this.deepRecalculate();
    },
    /*
     * Reload the suggestion/recipes attached to the selection
     */
    updateSelection(dishId, recipeIndex) {
      if (!dishId) {
        dishId = this.selection.dish.id;
      }
      const dish = this.dishById[dishId];

      const mealSlot = this.mealSlotById[dish.mealId];

      if (!recipeIndex || recipeIndex >= dish.recipes.length) {
        recipeIndex = 0;
      }

      // Retrieving ratio
      if (dish.recipes.length > 0) {
        // Already set recipe ratio
        const ratio = dish.recipes[recipeIndex].ratio;

        this.selection = {
          dish,
          ratio,
          recipeIndex,
          dishTypeId: dish.dishTypeIds[recipeIndex],
          mealSlot,
        };

        this.loadSelectionRecipe();
      } else {
        this.unselectRecipe();
      }

      this.updateStateToSuggestOrComplete();
    },
    /*
     * Recalculate everything from scratch
     */
    deepRecalculate(callback) {
      // There is one more dish (or one less). Content needs to be updated/recalculated
      this.reset(this.date, { recalculate: true, restartFromExisting: false }, callback);
    },
    /*
     * Optimize the solution by restarting from the existing one
     */
    recalculate(callback) {
      // There is one more dish (or one less). Content needs to be updated/recalculated
      this.reset(this.date, { recalculate: true, restartFromExisting: true, minimizeChange: "weak" }, callback, true);
    },
    /*
     * The user chooses not to reinitialize the day from metaplanning
     */
    ignoreConfigurationChange() {
      this.showConfigurationChangePopup = false;
    },
    showConfigurationChange() {
      this.showConfigurationChangePopup = true;
    },
    /*
     * The user chooses to reinitialize the day from the metaplanning
     */
    reinitFromMeta(hidePopup) {
      if (hidePopup) {
        this.ignoreConfigurationChange();
      }
      this.current.state = "please_wait";
      this.reset(this.date, { init: true, resetFromMetaplaning: true }, () => {
        this.$store.dispatch("shopping/update");
      });
    },
    onAddRecipe() {
      this.$store.dispatch("cookbook/createRecipe", { userId: this.userId, defaultName: this.search.keyword });
    },
  },
  components: {
    PleaseWait,
    Dialog,
    RatioPieChart,
    DaySelector,
    DayPlannerHeader,
    RecipeStats,
    DayIndicators,
    DayMosaic,
    DayMealPlaceEditor,
    SelectionBlock,
    ReplaceRecipeDialog,
  },
};
</script>

<style lang="scss">
$day-planner-content-spacing: 15px;

// End of patch

#please-wait-global {
  top: 0px;
  position: absolute;
  left: 0px;
  .op-please-wait {
    position: fixed;
    width: 100%;
    height: 100%;
    z-index: 120;
    background-color: rgba(0, 0, 0, 0.1);
    div {
      vertical-align: top !important;
    }
    img {
      margin-top: 200px;
      width: 100%;
      max-width: 600px;
    }
  }
}

#why-unbalanced,
#why-calories {
  .op-raw-table {
    margin-left: 15px;

    & > div {
      display: table-row;
      padding-bottom: 5px;
      line-height: 18px;
    }
    & > div > span {
      padding-top: 15px;
      display: table-cell;
    }
  }
}

#why-calories {
  font-size: $op-font-lg;
}

#recipe-selection-dialog {
  .modal-dialog {
    @media (min-width: $bootstrap-md-min) {
      min-width: 900px;
    }
  }

  .recipe-stats {
    background-color: $op-color-grey-light;
    margin-top: -15px;
    margin-bottom: -15px;
    padding: 0px !important;
    border-bottom-right-radius: 7px;
  }
}

#op-day-planner-page {
  .day-planner-page-content {
    margin: auto;
    padding: 0px;
    height: 100%;
    min-height: 500px;
    position: relative;

    &:after {
      @extend .clearfix;
    }
  }

  .day-planner-day-panel {
    background-color: $op-color-body-background;
    border-left: $op-page-content-border-width solid $op-color-border;
    border-right: $op-page-content-border-width solid $op-color-border;
    border-bottom: $op-page-content-border-width solid $op-color-border;
    &:after {
      @extend .clearfix;
    }
  }

  .day-planner-left-panel {
    background-color: $op-color-body-background;
    border-right: $op-page-content-border-width solid $op-color-border;
    padding: $day-planner-content-spacing;

    /*.transition(all, 0.4s, ease-in-out); */

    .op-day-mosaic {
      display: block;
    }

    .ok-btn {
      margin-top: 10px;
    }
  }

  .search-results {
    li {
      margin-top: 5px;
      text-decoration: underline;
      cursor: pointer;
    }
  }

  #too-much-in-future {
    padding: 50px;
    background-color: white;
    text-align: center;
    span {
      display: inline-block;
    }
    svg {
      margin-right: 20px;
    }
  }
}
</style>
