<template>
  <div id="ingredient-editor-page">
    <div id="add-ingredient">
      <FoodSearch style="display: inline-block" :onClickFood="onAddIngredient"> Ingrédient </FoodSearch>
    </div>

    <div class="recipe-edit-ingredients mt-2" v-show="ingredients.length > 0">
      <div class="op-table">
        <div class="op-header">
          <div class="ingredient-edit-spacer"></div>
          <!-- spacer -->
          <!-- modification is operators only -->
          <div class="ingredient-edit-icon-column"></div>
          <div class="ingredient-text"></div>
          <div class="ingredient-edit-food-quantity">Quantité</div>
          <div class="ingredient-edit-food-raw-state">Conditionnement</div>
          <div class="ingredient-edit-food-cooking-method">Cuisson appliquée</div>
          <div class="ingredient-options" v-if="hideOptions"></div>
          <div class="ingredient-edit-spacer"></div>
          <!-- spacer -->
        </div>
        <div
          class="op-row"
          v-for="(ingredient, index) in ingredientsReverse"
          :key="ingredient.id"
          :class="{ 'ingredient-even': index % 2 == 0, 'ingredient-odd': index % 2 == 1 }"
        >
          <!-- spacer -->
          <div class="ingredient-edit-spacer"></div>

          <!-- Food deletion button -->
          <div class="ingredient-edit-icon-column ingredient-first-row">
            <span class="ingredient-delete-btn" @click="deleteIngredient(ingredient)">
              <FontAwesomeIcon :icon="['fas', 'trash']" />
            </span>
          </div>

          <!-- Food name -->
          <div class="ingredient-text ingredient-first-row">
            <span>{{ ingredient.food.name }}</span>
          </div>

          <div class="ingredient-edit-food-quantity">
            <div class="input-group" v-if="ingredient.food.type != cookingConsumerGoodsFoodType">
              <!-- Numeric value for quantity -->
              <SmartFloatInput
                :modelValue="quantityConverted[ingredient.id]"
                @update:modelValue="onChangeQuantity(ingredient, $event)"
                class="form-control"
                :min="0"
              />
              <!-- Type of conversion -->
              <select
                v-model="defaultConversion[ingredient.id]"
                class="form-control form-select col-md-8"
                @change="onChangeConversion(ingredient)"
              >
                <option v-for="c in availableConversions[ingredient.id]" :value="c.id" :key="c.id">
                  {{ c.unit }}
                </option>
              </select>
            </div>
          </div>

          <!-- Raw state -->
          <div class="ingredient-edit-food-raw-state">
            <div class="centered-text" v-if="ingredient.food.type != cookingConsumerGoodsFoodType">
              <span class="ingredient-text centered-text" v-if="!showOptions[ingredient.id]">
                {{ rawStateName(ingredient) }}
              </span>
              <span v-if="showOptions[ingredient.id]" class="input-group">
                <select
                  v-model="rawState[ingredient.id]"
                  class="form-control form-select"
                  @change="saveIngredient(ingredient)"
                >
                  <option v-for="r in rawStates" :value="r.id" :key="r.id">
                    {{ r.name }}
                  </option>
                </select>
              </span>
            </div>
          </div>

          <!-- Cooking method -->
          <div class="ingredient-edit-food-cooking-method">
            <div class="centered-text" v-if="ingredient.food.type != cookingConsumerGoodsFoodType">
              <span class="ingredient-text" v-show="!showOptions[ingredient.id]">
                {{ cookingMethodName(ingredient) }}
              </span>
              <span v-if="showOptions[ingredient.id]" class="input-group">
                <Select2
                  :options="cookingMethodsAsOptions(ingredient)"
                  placeholder="Choisissez une cuisson"
                  :settings="{
                    multiple: false,
                    minimumResultsForSearch: -1,
                    templateSelection: cookingMethodFormat,
                    templateResult: cookingMethodFormat,
                    width: '100%',
                  }"
                  :modelValue="String(cookingMethod[ingredient.id])"
                  :preventSelect="(cookingMethod) => cookingMethod.id == 'more'"
                  @select="onChangeCookingMethod(ingredient, $event)"
                  :onSelecting="(event, select2) => onSelectCookingMethod(ingredient, event, select2)"
                />
              </span>
            </div>
          </div>

          <!-- Options -->
          <div class="ingredient-options">
            <span class="ingredient-text" @click="toggleOptions(ingredient)" v-if="hideOptions">
              <FontAwesomeIcon :icon="['fas', 'wrench']" />
            </span>
          </div>

          <!-- spacer -->
          <div class="ingredient-edit-spacer"></div>
        </div>
      </div>
    </div>
    <!-- recipe-edit-ingredients -->
  </div>
</template>

<script>
import Select2 from "@/components/interface/Select2.vue";
import FoodSearch from "@/components/recipe/FoodSearch.vue";
import SmartFloatInput from "@/components/interface/smart_inputs/SmartFloatInput.vue";
import { COOKING_CONSUMER_GOODS_FOOD_TYPE_ID } from "@/common/static.js";
import { upperFirst, find, union, sortBy } from "lodash";
import API from "@/api.js";
import $ from "jquery";

// If enabled, the ingredient quantity will be automatically converted to the new measure when changing conversion
const enableAutoQuantityConversion = false;

export default {
  name: "IngredientEditor",
  props: {
    recipe: {},
    hideOptions: { default: true }, // Hide cooking method and raw state by default
    ingredientList: {},
  },
  data: () => ({
    cookingConsumerGoodsFoodType: COOKING_CONSUMER_GOODS_FOOD_TYPE_ID,
    rawStates: [],
    ingredients: [],
    availableConversions: {},
    grams: {},
    cookingMethod: {},
    cookingMethods: {},
    defaultConversion: {},
    conversionsPerId: {},
    quantityConverted: {},
    showOptions: {},
    showAllCookingMethods: {},
    rawState: {},
    rawStatesOptions: {},
    cookingMethodsOptions: {}
  }),
  async mounted() {
    this.rawStates = await API.rawStates();
    await this.loadRecipeIngredients(this.ingredientList);
  },
  computed: {
    recipeNbPeople() {
      return this.recipe?.nbPeople;
    },
    ingredientsReverse() {
      return sortBy(this.ingredients, ['id']);
    },
    usePreviousCookingMethod() {
      return !this.hideOptions;
    },
  },
  watch: {
    async ingredientList(ingredientList, previousValue) {
      if (previousValue.length === 0) {
        await this.loadRecipeIngredients(ingredientList);
      }
    },
    recipeNbPeople(newNbPeople, oldNbPeople) {
      // When number of people change, update the quantities
      if (newNbPeople != oldNbPeople && newNbPeople) {
        this.updateAllIngredientsGrams();
      }
    },
  },
  methods: {
    upperFirst,
    /*
     * Load the recipe ingredient from the REST API
     */
    async loadRecipeIngredients(ingredientList) {
      this.ingredients = [];
      this.availableConversions = {};
      this.grams = {};
      this.cookingMethod = {};
      this.cookingMethods = {};
      this.conversionsPerId = {};
      this.quantityConverted = {};
      this.showAllCookingMethods = {};
      this.rawStatesOptions = {};
      this.cookingMethodsOptions = {};
      this.defaultConversion = {};
      this.rawState = {};
      for (const ingredient of ingredientList || []) {
        await this.initAndAddIngredient(ingredient, false);
      }
    },
    /*
     * Load conversions for an ingredient, and add it to the list of ingredients
     */
    async initAndAddIngredient(ingredient, appendIngredient = true) {
      this.availableConversions[ingredient.id] = [];
      this.grams[ingredient.id] = ingredient.grams;
      this.cookingMethod[ingredient.id] = ingredient.cookingMethod;
      this.rawState[ingredient.id] = ingredient.rawState;
      this.defaultConversion[ingredient.id] = ingredient.defaultConversion;
      this.cookingMethods[ingredient.id] = [];
      this.conversionsPerId[ingredient.id] = {};
      this.quantityConverted[ingredient.id] = 0;
      this.showOptions[ingredient.id] = this.showOptions[ingredient.id] || !this.hideOptions;
      this.showAllCookingMethods[ingredient.id] = false;
      this.rawStatesOptions[ingredient.id] = {};
      this.cookingMethodsOptions[ingredient.id] = {};

      // Check if ingredient already exists in list
      let j = 0;
      for (; j < this.ingredients.length; j++) {
        if (this.ingredients[j].id == ingredient.id) {
          break;
        }
      }
      if (j < this.ingredients.length) {
        this.ingredients[j] = ingredient;
      } else {
        if (appendIngredient) {
          this.ingredients.push(ingredient);
        } else {
          // Sorted insert
          let i = 0;
          for (; i < this.ingredients.length; i++) {
            if (this.grams[ingredient.id] > this.grams[this.ingredients[i].id]) {
              break;
            }
          }
          // Javascript equivalent of insert
          this.ingredients.splice(i, 0, ingredient);
        }
      }

      await this.refreshAvailableOptions(ingredient);
      await this.refreshAvailableConversions(ingredient);
      await this.refreshCookingMethods(ingredient);
    },
    async refreshAvailableOptions(ingredient) {
      const options = await API.food.availableOptions(ingredient.food.id);
      this.rawStatesOptions[ingredient.id] = options.rawStates;
      this.cookingMethodsOptions[ingredient.id] = options.cookingMethods;
    },
    async refreshAvailableConversions(ingredient) {
      const conversions = await API.foodConversion.searchByFood(ingredient.food.id);
      this.availableConversions[ingredient.id] = conversions;
      for (const conversion of conversions) {
        this.conversionsPerId[ingredient.id][conversion.id] = conversion;
      }
      this.updateQuantityConverted(ingredient);
    },
    async refreshCookingMethods(ingredient) {
      const data = await API.cookingMethod.food(ingredient.food.id);
      const available = [];
      const unavailable = [];
      for (const cm of data) {
        if (cm.id === this.cookingMethod[ingredient.id]) {
          cm.available = true;
        }
        if (cm.available) {
          available.push(cm);
        } else {
          unavailable.push(cm);
        }
      }
      const more = [{ id: "more", name: "", available: true }];
      this.cookingMethods[ingredient.id] = union(available, unavailable, more);
    },
    rawStateName(ingredient) {
      const state = find(this.rawStates, ["id", this.rawState[ingredient.id]]);
      return upperFirst(state?.name || "");
    },
    cookingMethodName(ingredient) {
      const cookingMethod = find(this.cookingMethods[ingredient.id], ["id", this.cookingMethod[ingredient.id]]);
      return upperFirst(cookingMethod?.name || "");
    },
    cookingMethodsAsOptions(ingredient) {
      return this.cookingMethods[ingredient.id].filter((cookingMethod) => {
        return (
          ((cookingMethod.available || this.showAllCookingMethods[ingredient.id]) && cookingMethod.id !== "more") ||
          (!this.showAllCookingMethods[ingredient.id] && cookingMethod.id === "more")
        );
      });
    },
    cookingMethodFormat(cookingMethod) {
      if (cookingMethod.id == "more") {
        return $(
          `<div class="d-flex justify-content-center align-items-center" style="font-weight: bold; position: relative;">
               <span style="position: absolute; left: 4px; font-size: 20px">+</span>
               <span style="font-size: 11px; margin-top: 1px; margin-left: 12px; display: inline-block;">autres cuissons</span>
           </div>`
        );
      }
      return cookingMethod.name;
    },
    onChangeCookingMethod(ingredient, cookingMethod) {
      this.cookingMethod[ingredient.id] = parseInt(cookingMethod.id, 10);
      this.saveIngredient(ingredient);
    },
    onSelectCookingMethod(ingredient, cookingMethod, select2) {
      if (cookingMethod.id != "more") {
        return;
      }
      this.showAllCookingMethods[ingredient.id] = true;
      setTimeout(() => {
        select2.select2("open");
      }, 0);
    },
    /*
     * Update the number of grams per person for all ingredients.
     * Raised when the number of people for a given recipe changes
     */
    updateAllIngredientsGrams() {
      for (const ingredient of this.ingredients) {
        const currentConversion = this.getCurrentConversion(ingredient);
        if (currentConversion) {
          this.updateGrams(ingredient);
        }
      }
    },
    /*
     * Update value of grams per person from converted value, conversion and number of people
     */
    updateGrams(ingredient) {
      this.grams[ingredient.id] =
        (this.quantityConverted[ingredient.id] * this.getCurrentConversion(ingredient).value) / this.recipe.nbPeople;
      this.saveIngredient(ingredient);
    },
    /*
     * Returns the conversion object from the defaultConversion id
     */
    getCurrentConversion(ingredient) {
      return this.conversionsPerId[ingredient.id][this.defaultConversion[ingredient.id]];
    },
    /*
     * When the quantity is changed, update this.grams[ingredient.id]
     */
    onChangeQuantity(ingredient, quantityConverted) {
      if (!quantityConverted) {
        return;
      }
      this.quantityConverted[ingredient.id] = quantityConverted;
      this.updateGrams(ingredient);
    },
    /*
     * When the conversion is changed, update quantityConverted
     */
    onChangeConversion(ingredient) {
      if (enableAutoQuantityConversion) {
        this.updateQuantityConverted(ingredient);
      }
      if (this.grams[ingredient.id] > 0) {
        this.updateGrams(ingredient);
      }
    },
    /*
     * Update converted value from grams per person, conversion and number of people
     */
    updateQuantityConverted(ingredient) {
      this.quantityConverted[ingredient.id] = Number(
        ((this.recipe.nbPeople * this.grams[ingredient.id]) / this.getCurrentConversion(ingredient).value).toFixed(2)
      );
    },
    /*
     * Add an ingredient to a recipe (by default 0g)
     */
    async onAddIngredient(food) {
      const newIngredient = {
        recipe: this.recipe.id,
        food: food.id,
        grams: 0,
      };

      if (this.ingredients.length > 0 && this.usePreviousCookingMethod) {
        // We already have some ingredients in the recipe and can reuse their cookingMethod.
        const lastIngredient = this.ingredients[this.ingredientList.length - 1];
        newIngredient.cookingMethod = this.cookingMethod[lastIngredient.id];
      } else {
        // No referent ingredient yet, using default database values
        await API.food.availableOptions(food.id);
      }

      // Create the ingredient on server side
      const data = await API.ingredient.save(newIngredient);
      // Insert back the detailed food data
      data.food = food;
      // Now it's created, add it in the recipe
      this.$emit("update:ingredientList", [...this.ingredientList, data]);
      // Update the variables around it
      await this.initAndAddIngredient(data);
    },
    /*
     * Remove an ingredient from a recipe
     * WARNING: index is index in ingredient, not [necessarily] in ingredientList, due to asynchronous loading
     */
    deleteIngredient(ingredient) {
      // Removing ingredient from the scope
      const ingredientIndex = this.ingredients.indexOf(ingredient);
      this.ingredients.splice(ingredientIndex, 1);
      // Removing ingredient server-side
      API.ingredient.remove(ingredient.id);
      // Removing it from the recipe object  (being careful to retrieve the right index)
      let index = null;
      for (let i = 0; i < this.ingredientList.length; ++i) {
        if (this.ingredientList[i].id === ingredient.id) {
          index = i;
          break;
        }
      }
      if (index != null) {
        this.$emit(
          "update:ingredientList",
          this.ingredientList.filter((_, i) => i != index)
        );
      } else {
        console.log("error: can't find ingredient in list", ingredient, this.ingredientList);
      }
    },
    saveIngredient(ingredient) {
      const payload = {
        ...ingredient,
        food: ingredient.food.id,
        grams: this.grams[ingredient.id],
        cookingMethod: this.cookingMethod[ingredient.id],
        defaultConversion: this.defaultConversion[ingredient.id],
        rawState: this.rawState[ingredient.id],
      };
      API.ingredient.update(ingredient.id, payload);

      const pos = this.ingredientList.map((i) => i.id).indexOf(ingredient.id);
      const newIngredientList = [...this.ingredientList];
      newIngredientList[pos] = { ...payload, food: ingredient.food };
      this.$emit("update:ingredientList", newIngredientList);
    },
    toggleOptions(ingredient) {
      this.showOptions[ingredient.id] = !this.showOptions[ingredient.id];
    },
  },
  components: { FoodSearch, Select2, SmartFloatInput },
};
</script>

<style scoped lang="scss">
#ingredient-editor-page {
  .cnf-warning {
    color: red;
    font-size: $op-font-xxs;
    font-weight: bold;
  }

  .ingredient-edit-icon-column {
    width: 20px;
    cursor: pointer;
    text-align: center;
  }

  .ingredient-delete-btn {
    color: $op-color-red;
    // Patch: to force line height when food_type is "Cuisine"
    margin: 20px 0px;
  }

  .ingredient-modify-btn {
    color: $op-color-orange;
  }

  .ingredient-text {
    padding-left: 5px;
    padding-right: 5px;
  }

  .centered-text {
    text-align: center;
  }

  .ingredient-edit-spacer {
    width: 10px;
  }

  .ingredient-edit-food-raw-state {
    width: 125px;
    .input-group {
      width: 100%;
    }
  }

  .ingredient-edit-food-cooking-method {
    width: 135px;
    .input-group {
      width: 100%;
      div {
        width: 100%;
      }
    }
  }

  .ingredient-edit-food-quantity {
    $input_size: 70px;
    $select_size: 220px;
    width: ($input_size + $select_size);
    border-collapse: collapse;

    .input-group {
      @media (max-width: $bootstrap-sm-max) {
        width: 100%;
      }
      @media (min-width: $bootstrap-md-min) {
        width: $input_size + $select_size;
      }
    }
    input {
      @media (max-width: $bootstrap-sm-max) {
        width: 20%;
      }
      @media (min-width: $bootstrap-md-min) {
        width: $input_size;
      }
      display: inline-block;
    }
    select {
      @media (max-width: $bootstrap-sm-max) {
        width: 80%;
      }
      @media (min-width: $bootstrap-md-min) {
        width: $select_size;
      }
      display: inline-block;
    }
  }

  .ingredient-options {
    &:hover {
      color: black;
      cursor: pointer;
    }
  }

  .recipe-edit-ingredients {
    op-table-auto {
      border-collapse: collapse;
      width: 100%;

      div:first-child {
        text-align: center;
      }
    }
  }

  .op-table {
    @media (min-width: $bootstrap-md-min) {
      .op-row {
        height: 53px;
        & > div {
          @include op-table-cell-text;
        }
      }
      .op-header {
        & > div {
          @include op-table-cell-text;
        }
      }
    }
    @media (max-width: $bootstrap-sm-max) {
      .ingredient-first-row {
        height: 55px;
        display: inline-flex !important;
        align-items: center;
      }
      .op-row {
      }
      .op-header {
        display: none;
      }
      .ingredient-edit-icon-column {
        display: inline-block;
        margin-left: 5px;
      }
      .ingredient-text {
        display: inline-block;
      }
      .ingredient-edit-food-quantity {
        width: 100%;
      }
      .ingredient-edit-food-raw-state {
        width: 45%;
        float: left;
      }
      .ingredient-edit-food-cooking-method {
        width: 45%;
        float: left;
      }
      .ingredient-options {
        width: 10%;
        float: right;
      }
    }
  }
}
</style>
