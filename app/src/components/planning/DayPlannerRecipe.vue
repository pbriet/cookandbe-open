<template>
  <div class="op-day-planner-recipe">
    <RecipeViewer
      v-if="selection.recipe"
      :recipeId="selection.recipe.id"
      :ratio="selection.ratio"
      :showDetails="showDetails"
      :showRatings="showDetails"
      :eaterIds="selection.mealSlot.eating"
    >
      <div class="smart-shopping-block-actions" v-if="state === 'show_recipe' && !preventEdition">
        <button
          class="btn btn-success"
          v-if="isCurrentRecipe"
          @click="validate(selection.dish, selection.recipe)"
          v-show="showValidateBtn && !isRecipeValidated"
        >
          <FontAwesomeIcon :icon="['fas', 'check']" /> J'en veux
        </button>
        <button
          class="btn btn-secondary"
          v-if="isCurrentRecipe && selection.recipe.internal === false"
          v-show="considerAllValidated || !isCurrentRecipe"
          @click="onNotNow(selection.recipe)"
        >
          <FontAwesomeIcon :icon="['fas', 'sync']" /> Autre proposition
        </button>
        <button
          class="btn btn-secondary"
          v-if="isCurrentRecipe && selection.recipe.internal === false"
          v-show="considerAllValidated || !isCurrentRecipe"
          @click="onDislike(selection.recipe)"
        >
          <FontAwesomeIcon :icon="['far', 'thumbs-down']" /> Je n'aime pas
        </button>
        <!--     <button class="btn btn-warning"
      v-if="selection.recipe.internal === false"
      @click="onDeleteRecipe(selection.dish, selection.recipe, selection.recipeIndex)">
      <FontAwesomeIcon :icon="['fas', 'times']" /> Pas de {{ (dishTypesById[selection.dish.dishTypeIds[selection.recipe_index]].name || "").toLowerCase() }}
    </button> -->
        <button class="btn btn-secondary" @click="onReplace">
          <FontAwesomeIcon :icon="['fas', 'search']" /> Choisir une recette
        </button>
      </div>

      <div class="recipe-dishtype-selection" v-if="state === 'select_dish_type'">
        Ajouter la recette en tant que :
        <button
          v-for="dishTypeId in selection.recipe.dishTypes"
          :key="dishTypeId"
          class="btn btn-success"
          @click="selectDishType(dishTypeId)"
        >
          {{ dishTypesById[dishTypeId].name }}
        </button>
        <button class="btn btn-secondary" @click="cancelDishtypeSelection">Annuler</button>
      </div>
    </RecipeViewer>
  </div>
</template>

<script>
import RecipeViewer from "@/components/recipe/recipe_viewer/RecipeViewer.vue";
import { RECIPE_PRICE_OPTIONS } from "@/common/static.js";
import { find } from "lodash";

/*
 * This component displays a suggestion in smart shopping
 */
export default {
  name: "DayPlannerRecipe",
  props: [
    "dishTypesById",
    "selection",
    "onAddRecipe",
    "onDislike",
    "onNotNow",
    "onReplace",
    "onDeleteRecipe",
    "considerAllValidated",
    "onValidate",
    "showValidateBtn",
    "showDetails",
    "preventEdition",
  ],
  data: () => ({
    PRICE_OPTIONS: RECIPE_PRICE_OPTIONS,
    state: "show_recipe",
    selectedDishTypeId: null,
  }),
  computed: {
    // Returns True if the displayed recipe is currently in the dish
    isCurrentRecipe() {
      if (!this.selection.dish) {
        return false;
      }
      for (let i = 0; i < this.selection.dish.recipes.length; i++) {
        if (!this.considerAllValidated && !this.selection.dish.recipes[i].validated) {
          continue;
        }
        if (this.selection.dish.recipes[i].id == this.selection.recipe.id) {
          return true;
        }
      }
      return false;
    },
    isRecipeValidated() {
      return this.selection.dish && find(this.selection.dish.recipes, ["id", this.selection.recipe.id]).validated;
    },
  },
  watch: {
    selection: {
      handler(newValue) {
        // When tree is initialized, or changes, update the data
        if (newValue) {
          this.init();
        }
      },
      deep: true,
    },
  },
  methods: {
    init() {
      this.state = "show_recipe";
      this.selectedDishTypeId = null;
    },
    addToBasket() {
      // Complex mode : make the recipe dishType match the given dish structure
      // If required, ask the user for the correct dish type
      let dishTypeId;
      if (this.selection.recipe.dishTypes.length == 1) {
        dishTypeId = this.selection.recipe.dishTypes[0];
      } else if (this.selectedDishTypeId) {
        dishTypeId = this.selectedDishTypeId;
      } else {
        this.state = "select_dish_type";
        return;
      }
      this.onAddRecipe(this.selection.recipe, dishTypeId);
    },
    selectDishType(dishTypeId) {
      this.selectedDishTypeId = dishTypeId;
      this.addToBasket();
    },
    validate(dish, recipe) {
      this.onValidate(dish, recipe);
    },
    cancelDishtypeSelection() {
      this.state = "show_recipe";
    },
  },
  components: { RecipeViewer },
};
</script>

<style lang="scss">
.op-day-planner-recipe {
  &:after {
    @extend .clearfix;
  }

  .smart-shopping-block-actions {
    padding: 5px 0px;
    clear: both;
    text-align: left;

    button {
      margin: auto;
      width: 170px;
      font-size: $op-font-sm;
      text-align: left;
      display: inline-block;
      margin: 5px;
    }

    svg {
      vertical-align: bottom;
      margin-right: 5px;
      font-size: $op-font-xxl;
    }
  }

  .recipe-img > div {
    width: $op-recipe-img-width-md;
    height: $op-recipe-img-height-md;
  }

  .recipe-properties {
    margin-top: 10px;
    margin-bottom: 5px;
    .glyphicon-time {
      font-size: $op-font-lg;
      line-height: $op-font-lg;
    }
    .glyphicon-euro {
      font-size: $op-font-lg;
      line-height: $op-font-lg;
    }
  }

  .recipe-quality {
    display: inline-block;
    border: 1px solid #cccccc;
    color: white;
    margin-left: 5px;
    padding: 2px 5px 2px 5px;
    background-color: $op-color-alert-ok;
  }

  .recipe-dishtype-selection {
    button {
      display: block;
      width: 300px;
      margin-top: 5px;
    }
  }
}
</style>
