<template>
  <!-- Add a new dish popup  -->
  <Dialog id="add-new-dish-popup" :open="showNewDishPopup" :onClose="closeNewDishPopup" :closeBtn="true">
    <AddNewDish v-if="selectedMealslot" :mealslot="selectedMealslot" :onCreated="onAddNewDish" />
  </Dialog>

  <!-- Show external meal suggestions  -->
  <Dialog
    id="external-meal-suggestions"
    :open="showExternalSuggestionsPopup"
    :onClose="closeExternalSuggestions"
    :closeBtn="true"
  >
    <div class="dialog-title">Nos conseils pour ce repas</div>
    <PleaseWait :until="externalSuggestions">
      <div class="dialog-body">
        <div class="op-vs">
          <table class="op-table">
            <tr v-for="suggestion in externalSuggestions.result" :key="suggestion.name">
              <td>{{ suggestion.grams }}g</td>
              <td>{{ suggestion.name }}</td>
            </tr>
          </table>
        </div>
        <div class="row">
          <div class="ms-auto col-6 col-sm-4 col-md-3">
            <div class="btn btn-success btn-block" @click="closeExternalSuggestions">Ok</div>
          </div>
        </div>
      </div>
    </PleaseWait>
  </Dialog>

  <!-- Edit mealslot eaters popup  -->
  <Dialog id="edit-eaters-popup" :open="showEditEatersPopup" :onClose="onEditedMealslotEaters" :closeBtn="true">
    <EditEaters
      v-if="selectedMealslot"
      :mealslotId="selectedMealslot.mealSlot.id"
      :withTitle="true"
      :mealslotEaterIds="selectedMealslot.mealSlot.eating"
      :onValidated="onEditedMealslotEaters"
    />
  </Dialog>

  <div class="meal-slot" v-for="mealslot in dayContent?.content || []" :key="mealslot.mealSlot.id">
    <!-- Meal title -->
    <div class="meal-slot-header row">
      <div class="col-8 col-md-4 mealslot-header-section">
        <span :class="{ 'op-clickable-link': !preventEdition }" @click="modifyMealPlace">
          <span class="meal-place">
            <img class="op-icon-xl" :src="placeImg(PLACES[mealslot.mealSlot.mealPlace.key].img)" />
          </span>
          <span class="meal-title">
            {{ mealslot.mealSlot.mealType.name }}
          </span>
        </span>
      </div>
      <div class="d-none d-sm-block col-md-5 mealslot-header-section">
        <div v-if="isMealslotSuggested(mealslot)">
          <MealSettings
            v-if="isSuggested(mealslot) && !preventEdition"
            :speedElt="mealslot.mealSlot"
            :eaters="mealslot.mealSlot.eating"
            :eatenAtHome="mealslot.mealSlot.eatenAtHome"
            :allowMealEdit="true"
            :onAddDish="() => addDish(mealslot)"
            :onChangeSpeed="(speed) => updateMealslotSpeed(mealslot, speed)"
            :onEditEaters="() => editMealslotEaters(mealslot)"
          />
        </div>
      </div>
      <div
        class="col-4 col-md-3 mealslot-header-section mealslot-header-action"
        @click="toggleShowSuggestions(mealslot)"
        v-if="!hasActivatedDishes(mealslot)"
      >
        <span>
          <span v-if="!isMealslotSuggested(mealslot)">Voir</span>
          <span v-if="isMealslotSuggested(mealslot)">Cacher</span>
          <span class="show_suggestions_explicit"> les suggestions</span>
        </span>
        <span class="ms-2">
          <FontAwesomeIcon :icon="['fas', 'chevron-right']" />
        </span>
      </div>
    </div>
    <span class="clearfix" />

    <div v-if="!mealslot.mealSlot.cookedAtHome" class="ms-2 mt-4">
      <h4>Repas à l'extérieur</h4>
      <a href="" class="btn btn-secondary" @click.prevent="showExternalSuggestions(mealslot.mealSlot)">
        Voir nos conseils pour ce repas
      </a>
    </div>

    <!-- Meal content -->
    <div class="mealslot-dishes" v-if="isMealslotSuggested(mealslot)">
      <!-- Dish -->
      <div
        class="dish"
        v-for="dish in mealslot.dishes"
        :key="dish.id"
        :class="{ 'non-activated-dish': !dish.activated, 'activated-dish': dish.activated }"
      >
        <!-- Dish header -->
        <div class="row dish-header" v-if="dish.recipes.length > 0">
          <!-- Dish image (first dishrecipe) -->
          <div class="col-3 col-sm-2 col-lg-1 dish-header-left" @click="toggleDishActivation(mealslot, dish)">
            <div class="in-basket-indicator" v-show="dish.recipes[0].inShoppingList">
              <FontAwesomeIcon :icon="['fas', 'shopping-basket']" />
            </div>
            <RecipeImg :recipe="dish.recipes[0]" :withBorder="true" :disc="true" />
          </div>

          <!-- Dish name and show  button -->
          <div class="dish-header-right col-9 col-sm-10 col-lg-11">
            <button
              class="dish-toggle-btn btn btn-success op-font-xl show-more-dish"
              v-if="!dish.activated"
              @click="toggleDishActivation(mealslot, dish)"
            >
              <FontAwesomeIcon :icon="['fas', 'angle-double-down']" />
            </button>
            <button
              class="dish-toggle-btn btn btn-secondary op-font-xl show-more-dish"
              v-if="dish.activated"
              @click="toggleDishActivation(mealslot, dish)"
            >
              <FontAwesomeIcon :icon="['fas', 'angle-double-up']" />
            </button>

            <span class="dish-header-text">
              {{ upperFirst(getDishName(dish.dishTypeIds[0])) }}

              <span class="dish-recipe-names">
                <span v-for="(recipe, index) in dishRecipes(dish)" :key="recipe.id">
                  <span v-if="index > 0"> + </span>
                  <span v-if="index == 0"> : </span>
                  <span class="recipe-name">{{ recipe.name }}</span>
                </span>
              </span>
            </span>
          </div>
        </div>
        <!-- !dish-header -->

        <div class="dishrecipes" v-if="dish.activated">
          <div class="dishrecipe row" v-for="(recipe, index) in dishRecipes(dish)" :key="recipe.Id">
            <div class="d-none d-sm-block col-sm-2 col-lg-1"></div>
            <!-- Blank space : same size as small images -->

            <!-- dish-slot -->

            <div
              class="dish-big-img col-4 col-sm-3 col-md-3"
              @click="onSelectDish(dish.id, recipe, true)"
              :class="{
                'selected-dishslot':
                  selection && selection.dish && selection.dish.id === dish.id && selection.recipeIndex === index,
                'non-selected-dishslot':
                  selection && selection.dish && (selection.dish.id !== dish.id || selection.recipeIndex !== index),
              }"
            >
              <div
                class="dish-action-btn favorite-recipe-btn d-none d-sm-block"
                v-if="!preventEdition && isSuggested(mealslot)"
                :class="{ 'is-favorite': recipeIsFavorite(recipe.id) }"
                @click.stop="toggleFavorite(recipe)"
              >
                <FontAwesomeIcon :icon="['fas', 'heart']" />
              </div>

              <div class="dish-action-btns d-none d-sm-block" v-if="!preventEdition && isSuggested(mealslot)">
                <span class="dish-action-btn" @click.stop="onSelectDish(dish.id, recipe, true)">
                  <FontAwesomeIcon :icon="['fas', 'edit']" size="sm" />
                </span>
                <span class="dish-action-btn" v-if="!preventEdition" @click.stop="onNotNow(recipe, dish.id)">
                  <FontAwesomeIcon :icon="['fas', 'sync']" size="sm" />
                </span>
              </div>

              <!-- Picture -->
              <RecipeImg :recipe="recipe" :withBorder="true" :disc="true">
                <div class="overlay-row" v-if="recipe.validated">
                  <div class="overlay-cell text-center">Recette validée</div>
                </div>
                <div class="overlay-row" v-if="recipe.modified">
                  <div class="overlay-cell text-center">Modifié</div>
                </div>
                <div class="overlay-row-void"></div>
              </RecipeImg>
            </div>
            <!-- clickable-dish-slot -->

            <!-- Toolbar for mobile -->
            <div class="d-sm-none col-4 col-sm-6 mobile-dish-toolbar">
              <div class="btn btn-secondary d-sm-none" @click.stop="onNotNow(recipe, dish.id)" v-if="!preventEdition">
                <FontAwesomeIcon :icon="['fas', 'sync']" />
              </div>
            </div>
            <div class="activated-recipe-infos col-12 col-sm-7 col-md-7 col-lg-8">
              <div class="recipe-name">
                {{ recipe.name }}
              </div>

              <div class="recipe-info" v-show="recipe.avgRating">
                <RatingStars :value="recipe.avgRating" />
              </div>
              <div class="recipe-info">
                <span
                  v-for="(option, priceIndex) in RECIPE_PRICE_OPTIONS"
                  :key="option.id"
                  v-show="priceIndex < recipe.price"
                  class="me-1"
                >
                  <FontAwesomeIcon :icon="['fas', 'euro-sign']" />
                </span>
                <span v-for="option in RECIPE_PRICE_OPTIONS" :key="option.id" v-show="option.id === recipe.price">
                  &nbsp;{{ option.label }}
                </span>
              </div>
              <div class="recipe-info">
                <span
                  v-for="(option, difficultyIndex) in RECIPE_DIFFICULTY_OPTIONS"
                  :key="option.id"
                  v-show="difficultyIndex < recipe.difficulty"
                  class="me-1"
                >
                  <FontAwesomeIcon :icon="['fas', 'flask']" />
                </span>
                <span
                  v-for="option in RECIPE_DIFFICULTY_OPTIONS"
                  :key="option.id"
                  v-show="option.id === recipe.difficulty"
                >
                  &nbsp;{{ option.label }}
                </span>
              </div>
              <div class="shopping-btn-switch">
                <ToggleSwitch
                  v-model="recipe.inShoppingList"
                  :readonly="preventEdition !== null"
                  :onChange="() => toggleShoppingDishrecipe(dish, recipe)"
                />
                Dans ma liste de courses
              </div>
            </div>
            <!-- activated-recipe-infos -->

            <div class="col-4 d-sm-none"></div>
          </div>
          <!-- recipe -->
        </div>
        <!-- recipes -->
      </div>
      <!-- dish -->
    </div>
    <!-- mealslot-dishes -->
  </div>
</template>

<script>
import API from "@/api.js";
import { PLACES } from "@/common/static.js";
import { mapGetters } from "vuex";
import { RECIPE_PRICE_OPTIONS, RECIPE_SPEED_OPTIONS, RECIPE_DIFFICULTY_OPTIONS } from "@/common/static.js";
import { upperFirst, find, take } from "lodash";
import Dialog from "@/components/interface/Dialog.vue";
import ToggleSwitch from "@/components/interface/ToggleSwitch.vue";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import AddNewDish from "@/components/planning/AddNewDish.vue";
import EditEaters from "@/components/planning/EditEaters.vue";
import MealSettings from "@/components/planning/MealSettings.vue";
import RecipeImg from "@/components/recipe/RecipeImg.vue";
import RatingStars from "@/components/interface/RatingStars.vue";

/*
 * This component displays a day being filled in smart shopping
 */
export default {
  name: "DayMosaic",
  props: [
    "date", // Current date
    "selection",
    "dayContent", // Content of this day (mealslots, dishes, ...)
    "suggestionsByDishid", // For each dish, what are the suggestions
    "dishTypesById",
    "selectedDishId", // What is the currently selected dish id
    "onSelectDish", // Handler when a dish is selected
    "onNotNow", // Handler when "not now" button is clicked
    "onNewDish",
    "onChangeMealSpeed",
    "onChangeMealEaters",
    "onModifyMealPlace",
    "preventEdition", // Is it possible to edit the planning
  ],
  data: () => ({
    PLACES,
    RECIPE_PRICE_OPTIONS,
    RECIPE_SPEED_OPTIONS,
    RECIPE_DIFFICULTY_OPTIONS,
    selectedMealslot: null,
    externalSuggestions: null,
    showNewDishPopup: false,
    showExternalSuggestionsPopup: false,
    showEditEatersPopup: false,
  }),
  computed: {
    ...mapGetters({
      userId: "user/id",
      dishTypes: "cache/getDishTypes",
      recipeIsFavorite: "cookbook/recipeIsFavorite",
    }),
  },
  methods: {
    upperFirst,
    dishRecipes(dish) {
      return take(dish.recipes, dish.dishTypeIds.length);
    },
    /*
     * The user clicks on the "+" to add a dish in a given mealslot
     * Show a popup to select its characteristics  (dishType essentially)
     */
    addDish(mealslot) {
      this.selectedMealslot = mealslot;
      this.showNewDishPopup = true;
    },
    closeNewDishPopup() {
      this.showNewDishPopup = false;
    },
    onAddNewDish(dishTypeId) {
      this.onNewDish(dishTypeId);
      this.closeNewDishPopup();
    },
    isMealslotSuggested(mealslot) {
      return mealslot.showSuggestions || this.hasActivatedDishes(mealslot);
    },
    toggleShowSuggestions(mealslot) {
      mealslot.showSuggestions = !mealslot.showSuggestions;
    },
    hasActivatedDishes(mealslot) {
      if (!mealslot.mealSlot.cookedAtHome) {
        return true;
      }
      for (let i = 0; i < mealslot.dishes.length; i++) {
        if (mealslot.dishes[i].activated) {
          return true;
        }
      }
      return false;
    },
    toggleDishActivation(mealslot, dish) {
      if (dish.activated) {
        // Cheating, making sure that the meal won't be hidden
        mealslot.showSuggestions = true;
      }
      dish.activated = !dish.activated;
      API.userDay.toggleDishActivation(this.userId, dish.id);
    },
    isSuggested(mealslot) {
      return mealslot.status == "suggested";
    },
    async updateMealslotSpeed(mealslot, speed) {
      const data = await API.mealSlot.setSpeed(mealslot.mealSlot.id, { speed });
      this.onChangeMealSpeed(mealslot, speed, data.previousValue);
    },
    modifyMealPlace() {
      if (this.preventEdition) {
        return;
      }
      this.onModifyMealPlace();
    },
    showExternalSuggestions(mealSlot) {
      API.mealSlot.externalSuggest(mealSlot.id).then((data) => {
        this.externalSuggestions = data;
      });
      this.showExternalSuggestionsPopup = true;
    },
    closeExternalSuggestions() {
      this.showExternalSuggestionsPopup = false;
    },
    editMealslotEaters(mealslot) {
      this.selectedMealslot = mealslot;
      this.showEditEatersPopup = true;
    },
    onEditedMealslotEaters() {
      const mealslot = this.selectedMealslot;
      this.onChangeMealEaters(mealslot);
      this.showEditEatersPopup = false;
    },
    toggleShoppingDishrecipe(dish, dishrecipe) {
      if (dishrecipe.inShoppingList === dishrecipe.previousShoppingState) {
        return;
      }
      dishrecipe.previousShoppingState = dishrecipe.inShoppingList;
      API.userDay.toggleDishrecipeShopping(this.userId, dish.id, { recipeId: dishrecipe.id });
    },
    toggleFavorite(recipe) {
      if (this.recipeIsFavorite(recipe.id)) {
        this.$store.dispatch("cookbook/rmRecipe", recipe.id);
      } else {
        this.$store.dispatch("cookbook/addRecipe", recipe.id);
      }
    },
    getDishName(dishTypeId) {
      return find(this.dishTypes(), ["id", dishTypeId])?.name || "";
    },
    placeImg(place) {
      return require(`@/assets/img/${place}`);
    },
  },
  components: { Dialog, PleaseWait, AddNewDish, RecipeImg, RatingStars, EditEaters, MealSettings, ToggleSwitch },
};
</script>

<style scoped lang="scss">
$dish-slot-margin: 3px;
$dish-slot-width: math.div($bootstrap-xs-max, 3);
$dish-slot-height: $op-recipe-img-height-xs + 10px;
$dish-slot-area-width: $dish-slot-margin * 2 + $dish-slot-width + 1px;

.meal-title {
  font-size: $op-font-lg;
  display: inline-block;
  padding-top: 5px;
}

.meal-place {
  vertical-align: bottom;
  display: none;
}

.mealslot-header-action {
  &:hover {
    background-color: white;
    color: $op-color-lime;
    cursor: pointer;
    border: solid 1px $op-color-lime;
    border-right: none;
    border-radius: 8px;
  }
  height: 32px;
  font-weight: 900;
  border-left: 1px solid white;
  padding-top: 7px !important;
  text-align: right;
  .show_suggestions_explicit {
    @media (max-width: 1380px) {
      display: none;
    }
  }
}

.mealslot-dishes {
  padding-bottom: 20px;
  padding-left: 5px;
}

.meal-slot-header {
  margin-left: 5px;
  margin-right: 5px;
  height: 32px;
  margin-bottom: 10px;
  background-color: $op-color-lime;
  color: white;
  padding-left: 10px;
  vertical-align: middle;
  border-radius: 8px;
  font-family: "quicksandbook", sans-serif;
  text-transform: uppercase;
  font-weight: bold;

  .suggested {
    text-decoration: underline;
    font-weight: bold;
  }

  .meal-settings {
    padding-top: 4px;
  }
}

.meal-slot {
  margin-bottom: 10px;
}

.dish {
  display: block;

  .dish-header {
    .in-basket-indicator {
      border-radius: 20px;
      background-color: white;
      position: absolute;
      bottom: 0px;
      z-index: 999;
      right: 20px;
      padding: 3px;
      color: $op-color-lime;
    }

    .show-more-dish {
      display: inline-block;
      padding: 0px 8px 3px 8px;
    }
    .dish-header-left {
      cursor: pointer;
    }

    .dish-header-right {
      padding-top: 10px;
      font-size: $op-font-md;
    }
    .dish-header-text {
      padding-left: 5px;
    }
  }
}
.non-activated-dish {
  .dish-header-right .recipe-name {
    font-weight: bold;
  }
}
.activated-dish {
  .dish-recipe-names {
    display: none;
  }
  .dish-header-text {
    font-style: italic;
  }
}

@media (max-width: $bootstrap-xs-max) {
  .activated-dish .dish-header-text,
  .activated-dish .dish-header-left {
    display: none !important;
  }
  .dishrecipe .dish-big-img {
    border-left: none !important;
    padding-bottom: 0px !important;
  }
  .dishrecipe {
    padding-bottom: 30px !important;
  }
  .activated-dish {
    padding-top: 20px;
  }
  .activated-recipe-infos .recipe-name {
    font-size: $op-font-xl !important;
  }

  .activated-dish .dish-header {
    float: right;
  }
  .non-activated-dish .dish-toggle-btn {
    float: right;
  }
  .activated-dish .dish-toggle-btn {
    background-color: $op-color-red !important;
    color: white !important;
  }
}

.non-selected-dishslot {
  opacity: 0.9;
}

.dish-slot-add {
  color: #bbbbbb;
}
.mobile-dish-toolbar {
  margin-top: 35px;
  .btn {
    margin: auto;
    width: 60px;
  }
}

.dishrecipe {
  margin: $dish-slot-margin;
  font-weight: bold;

  recipe-img {
    .overlay-table {
      text-align: center;
    }
  }

  &:hover {
    color: black;
  }

  .activated-recipe-infos {
    font-weight: normal;
    font-size: 14px;
    margin-top: 10px;
    img {
      width: 20px;
    }
    .recipe-info {
      margin-top: 5px;
    }
  }

  .recipe-name {
    font-weight: bold;
    font-size: 22px;
    margin-bottom: 4px;
  }
  .activated-recipe-dishtype {
    font-weight: normal;
    font-size: 16px;
    line-height: 16px;
    font-style: italic;
  }

  .shopping-btn-switch {
    padding-top: 10px;
  }

  .dish-big-img {
    position: relative;
    cursor: pointer;
    padding-left: 10px;
    padding-bottom: 30px;
    border-left: solid 1px #ccc;

    .dish-action-btn {
      cursor: pointer;
      color: white;
      text-align: center;
      border-radius: 20px;
      &:hover {
        background-color: white !important;
        color: $op-color-text-main;
      }

      font-size: 22px;
      display: inline-block;
      overflow: hidden;
    }

    .favorite-recipe-btn {
      position: absolute;
      right: 15%;
      top: 10%;
      z-index: 50;
      background-color: $op-color-grey-dark;
      &.is-favorite {
        background-color: $op-color-alert-danger;
      }
      width: 25px;
      height: 25px;
      font-size: 13px;
      padding-top: 3px;
      @media (max-width: $bootstrap-xs-max) {
        width: 25%;
        height: 25%;
        font-size: 26px;
        right: 5%;
        top: 5%;
      }
    }
    .dish-action-btns {
      position: absolute;
      width: 100%;
      height: 15%;
      bottom: 16px;
      text-align: center;
      z-index: 50;
      span {
        background-color: $op-color-lime;
        width: 35px;
        height: 35px;
        margin-left: -5%;
        margin-right: 6%;
      }
    }
  }
}

#external-meal-suggestions {
  td {
    padding: 10px;
  }
}
</style>
