<template>
  <Dialog :open="showRecipeEditUstensils" :closeBtn="true" :onClose="onCloseUstensilsEditor">
    <div class="dialog-title">Sélectionnez les ustensiles requis pour réaliser votre recette.</div>
    <div class="dialog-body">
      <EquipmentEditor :userUstensils="recipe?.ustensils" :onToggleUstensil="onToggleUstensil" />
      <button class="btn btn-success action-button fright" @click="onCloseUstensilsEditor">Ok</button>
      <span class="clearfix" />
    </div>
  </Dialog>

  <div id="recipe-edit-page" class="op-page">
    <div class="op-page-title">
      <h1>{{ getRecipeName }}</h1>
      <p>Éditeur de recettes</p>
    </div>
    <div id="recipe-edit-content" class="op-page-content">
      <!-- Header -->
      <div class="col-12">
        <RecipeEditToolbar :saveRecipe="saveRecipe" :errorStatus="errorStatus" />
      </div>

      <!-- Settings -->
      <div class="row">
        <div class="col-12">
          <h2>Paramètres</h2>
        </div>
        <div class="col-12">
          <div class="input-group">
            <span class="input-group-text">Nom de la recette</span>
            <input
              class="form-control h-100"
              placeholder="Ma recette"
              v-if="recipe"
              v-model="recipe.name"
              required
              type="text"
            />
          </div>
        </div>

        <div class="col-12 col-md-6 col-lg-3">
          <div class="input-group" style="width: 100%">
            <Select2
              :options="getDishTypes"
              placeholder="Choisissez un type de plat"
              :settings="{
                templateSelection: dishTypeFormat,
                templateResult: dishTypeFormat,
                multiple: false,
                containerCssClass: 'form-control w-100',
                width: '100%',
              }"
              v-if="recipe"
              :modelValue="recipe.dishTypes"
              @select="onSelectDishType"
              @unselect="onRemoveDishType"
            />
          </div>
        </div>

        <div class="col-12 col-md-6 col-lg-3">
          <div class="input-group">
            <span class="input-group-text"><img src="@/assets/img/recipe/people.png" /></span>
            <input
              class="form-control h-100"
              v-if="recipe"
              v-model.number="recipe.nbPeople"
              type="number"
              required
              min="1"
              max="20"
            />
            <span class="input-group-text">personne(s)</span>
          </div>
        </div>

        <div class="col-12 col-md-6 col-lg-3">
          <div class="input-group d-flex">
            <span class="input-group-text"><img src="@/assets/img/recipe/toque.png" /></span>
            <Select2
              :options="recipeDifficultyOptions"
              placeholder="Indiquez la difficulté"
              :settings="{
                templateSelection: difficultyFormat,
                templateResult: difficultyFormat,
                multiple: false,
                minimumResultsForSearch: -1,
                containerCssClass: 'form-control',
                width: 'auto',
              }"
              v-if="recipe"
              v-model="recipe.difficulty"
            />
          </div>
        </div>

        <div class="col-12 col-md-6 col-lg-3">
          <div class="input-group d-flex">
            <span class="input-group-text"><img src="@/assets/img/recipe/cost.png" /></span>
            <Select2
              :options="recipePriceOptions"
              placeholder="Indiquez le prix"
              :settings="{
                formatSelection: priceFormat,
                formatResult: priceFormat,
                multiple: false,
                minimumResultsForSearch: -1,
                containerCssClass: 'form-control',
                width: 'auto',
              }"
              v-if="recipe"
              v-model="recipe.price"
            />
          </div>
        </div>
      </div>
      <!-- Settings -->

      <!-- Time -->
      <div class="row">
        <div class="col-12">
          <h2>Temps</h2>
        </div>
        <span class="col-12 d-sm-none">(en minutes)</span>

        <div class="col-12 col-lg-4">
          <div class="input-group">
            <span class="input-group-text d-none d-sm-inline"><img src="@/assets/img/recipe/time.png" /></span>

            <span class="input-group-text recipe-edit-time-label">Préparation</span>
            <input
              class="form-control h-100"
              v-if="recipe"
              v-model.number="recipe.prepMinutes"
              required
              min="0"
              max="240"
              type="number"
            />
            <span class="input-group-text d-none d-sm-inline">minutes</span>
          </div>
        </div>

        <div class="col-12 col-lg-4">
          <div class="input-group">
            <span class="input-group-text d-none d-sm-inline"><img src="@/assets/img/recipe/time.png" /></span>

            <span class="input-group-text recipe-edit-time-label">Cuisson</span>
            <input
              class="form-control h-100"
              v-if="recipe"
              v-model.number="recipe.cookMinutes"
              required
              min="0"
              max="240"
              type="number"
            />
            <span class="input-group-text d-none d-sm-inline">minutes</span>
          </div>
        </div>

        <div class="col-12 col-lg-4">
          <div class="input-group">
            <span class="input-group-text d-none d-sm-inline"><img src="@/assets/img/recipe/time.png" /></span>

            <span class="input-group-text recipe-edit-time-label">Repos</span>
            <input
              class="form-control h-100"
              v-if="recipe"
              v-model.number="recipe.restMinutes"
              required
              min="0"
              max="4000"
              type="number"
            />
            <span class="input-group-text d-none d-sm-inline">minutes</span>
          </div>
        </div>
      </div>

      <!-- Ingredients -->
      <div class="row">
        <div class="col-12">
          <h2>Ingrédients</h2>
        </div>
        <div class="col-12">
          <p>
            Ajoutez un par un les ingrédients utilisés par votre recette. Pour chacun d'eux, renseignez la quantité
            ainsi que la façon dont il sera cuisiné !
          </p>
          <IngredientEditor
            v-if="recipe"
            :recipe="recipe"
            :hideOptions="false"
            v-model:ingredientList="ingredientList"
          />
        </div>
      </div>

      <!-- Instructions -->
      <div class="row">
        <div class="col-12">
          <h2>Instructions</h2>
        </div>
        <div class="col-12">
          <p class="mb-2">Décrivez chaque étape nécessaire à la réalisation de votre recette.</p>
          <div class="recipe-edit-instructions">
            <div
              class="recipe-edit-instruction d-flex align-items-center"
              v-for="(instruction, index) in recipeInstructions"
              :key="instruction.id"
            >
              <div class="recipe-edit-instruction-number">{{ index + 1 }}.</div>
              <input class="recipe-edit-instruction-text mb-2" v-model="instruction.text" />
            </div>
            <div class="col-md-12 recipe-edit-add-instruction-btn">
              <button class="btn btn-success" @click="onAddInstruction(true)">+</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Characteristics -->
      <div class="row">
        <div class="col-12">
          <h2>Caractéristiques</h2>
        </div>
        <div class="col-12">
          <div id="recipe-edit-ustensils" class="col-md-12 row">
            <div class="recipe-edit-question col-12 col-md-6">
              Votre recette nécessite-t-elle des ustensiles particuliers ?
            </div>
            <button class="btn btn-success col-12 col-sm-6 col-md-3" @click="onOpenUstensilsEditor">
              Choisir les ustensiles requis
            </button>
            <span class="col-12 col-sm-6 col-md-3">
              (actuellement :
              <b>
                <span v-if="recipe" v-show="recipe.ustensils.length <= 1">{{ recipe.ustensils.length }} ustensile</span>
                <span v-if="recipe" v-show="recipe.ustensils.length > 1">{{ recipe.ustensils.length }} ustensiles</span>
              </b>
              )
            </span>
          </div>

          <div id="recipe-edit-tags" class="col-md-12 row">
            <div class="recipe-edit-question col-md-6 col-12">Que peut-on dire de votre recette ?</div>
            <div class="col-md-6 col-12 p-0 mt-2">
              <TreeCombo
                :tree="simpleTags"
                v-if="recipe"
                v-model="recipe.tags"
                :multiple="true"
                :eraseBtn="true"
                placeholder="Caractéristique"
                :onAdd="onAddTag"
                :onRemove="onRemoveTag"
              />
            </div>
          </div>

          <div id="recipe-edit-location" class="col-md-12 row">
            <div class="recipe-edit-question col-md-6 col-12">Votre recette est-elle associée à une région ?</div>
            <div class="col-md-6 col-12 p-0">
              <div class="btn-group">
                <button
                  type="button"
                  class="btn"
                  @click="onChangeRecipeSpeciality(false)"
                  :class="{ 'btn-success disabled': !recipe?.origin, 'btn-secondary': recipe?.origin }"
                >
                  Non
                </button>
                <button
                  type="button"
                  class="btn"
                  @click="onChangeRecipeSpeciality(true)"
                  :class="{ 'btn-success disabled': recipe?.origin, 'btn-secondary': !recipe?.origin }"
                >
                  Oui
                </button>
              </div>
            </div>
            <TreeCombo
              :tree="locationTree"
              v-model="recipe.origin"
              :eraseBtn="true"
              class="col-md-12 mt-2 location-tree"
              v-if="recipe"
              v-show="recipe.origin"
              placeholder="Selectionnez ou entrez une localité"
            />
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="col-12">
        <RecipeEditToolbar :saveRecipe="saveRecipe" :errorStatus="errorStatus" />
      </div>
    </div>
  </div>
</template>

<script>
import API from "@/api.js";
import Dialog from "@/components/interface/Dialog.vue";
import RecipeEditToolbar from "@/components/recipe/RecipeEditToolbar.vue";
import EquipmentEditor from "@/components/config/EquipmentEditor.vue";
import IngredientEditor from "@/components/recipe/IngredientEditor.vue";
import Select2 from "@/components/interface/Select2.vue";
import TreeCombo from "@/components/interface/TreeCombo.vue";
import { mapGetters } from "vuex";
import {
  RECIPE_PRICE_OPTIONS,
  RECIPE_DIFFICULTY_OPTIONS,
  COOKING_CONSUMER_GOODS_FOOD_TYPE_ID,
  DEFAULT_RECIPE_NAME,
  RECIPE_STATUS,
  FRANCE_LOCATION_ID,
} from "@/common/static.js";
import { find, sortBy, includes } from "lodash";
import { sentenceTypoCheck } from "@/common/string.js";
import $ from "jquery";

const STATUS_REVIEW = find(RECIPE_STATUS, ["label", "Revue"]).id;
const STATUS_VALIDATED = find(RECIPE_STATUS, ["label", "Validée"]).id;

/*
 * Component for editing a recipe
 * Features:
 * - Modifying core recipe attributes (cooking time, difficulty, title, intructions, ...)
 * - Adding/removing an ingredient, including search by keyword and FoodType
 * - Setting quantities with different conversions
 */
export default {
  name: "RecipeEditor",
  props: [],
  data: () => ({
    showRecipeEditUstensils: false,
    errorStatus: null,
    recipe: {
      name: "",
      dishTypes: [],
      nbPeople: 1,
      difficulty: 1,
      price: 1,
      prepMinutes: 0,
      cookMinutes: 0,
      restMinutes: 0,
      instructions: [],
      ustensils: [],
      tags: [],
      origin: null,
    },
    simpleTags: [],
    treeTags: [],
    ingredientList: [],
    defaultOrigin: FRANCE_LOCATION_ID,
    RECIPE_PRICE_OPTIONS,
    RECIPE_DIFFICULTY_OPTIONS,
  }),
  mounted() {
    API.recipe.get(this.$route.params.recipeId, { details: "full" }).then((recipe) => {
      this.recipe = recipe;
      this.onRecipeLoaded();
    });

    // Available Recipe tags  (meat, beef, sweet and salt, Christmas, ...)
    API.recipeTags({ tree: 1 }).then((recipeTagsTree) => {
      this.classifyTags(recipeTagsTree);
    });
  },
  beforeRouteLeave(to, from, next) {
    /* Clear the cached values when leaving the page
     */
    this.$store.commit("recipe/clearCached", this.$route.params.recipeId);
    next();
  },
  computed: {
    ...mapGetters({
      dishTypes: "cache/getDishTypes",
      // Countries and continents
      locationTree: "cache/getLocations",
    }),
    getDishTypes() {
      // Ordering and filtering dish types
      const dishTypes = [];

      for (const dt of this.dishTypes()) {
        if (!dt.system) {
          dishTypes.push({ ...dt, text: dt.name });
        }
      }
      dishTypes.sort((x, y) => {
        if (x.text > y.text) {
          return 1;
        }
        if (x.text < y.text) {
          return -1;
        }
        return 0;
      });
      return dishTypes;
    },
    recipePriceOptions() {
      return RECIPE_PRICE_OPTIONS.map((option) => ({ ...option, text: option.label }));
    },
    recipeDifficultyOptions() {
      return RECIPE_DIFFICULTY_OPTIONS.map((option) => ({ ...option, text: option.label }));
    },
    getRecipeName() {
      if (!this.recipe) {
        return "";
      }
      if (!this.recipe.name) {
        return DEFAULT_RECIPE_NAME;
      }
      return this.recipe.name;
    },
    recipeInstructions() {
      if (!this.recipe) return [];
      return sortBy(this.recipe.instructions, (instruction) => instruction.id);
    },
  },
  methods: {
    onCloseUstensilsEditor() {
      this.showRecipeEditUstensils = false;
    },
    onOpenUstensilsEditor() {
      this.showRecipeEditUstensils = true;
    },
    dishTypeFormat(item) {
      return item.text;
    },
    difficultyFormat(item) {
      return item.text;
    },
    priceFormat(item) {
      return item.text;
    },
    onRecipeLoaded() {
      // Validation on save
      if (this.recipe.status < STATUS_REVIEW) {
        this.recipe.status = STATUS_VALIDATED;
      }
      if (this.recipe.name == DEFAULT_RECIPE_NAME) {
        this.recipe.name = "";
      }
      this.initIngredientList();
      this.initInstructionList();
    },
    /*
     ** Ingredients can't stay in the recipe, because the save function doesn't allow nested data...
     */
    initIngredientList() {
      this.ingredientList = this.recipe.ingredients;
      delete this.recipe.ingredients;
    },
    initInstructionList() {
      // Adding default empty instruction if none
      if (this.recipe.instructions.length === 0) {
        this.onAddInstruction(false);
      }
    },
    async onAddInstruction(setFocus) {
      const newInstruction = await API.recipeInstruction.save({
        recipe: this.recipe.id,
        text: " ", // Trick: instructions can't be null server side
      });
      this.recipe.instructions.push(newInstruction);

      if (setFocus) {
        setTimeout(() => {
          $("input.recipe-edit-instruction-text")
            .eq(this.recipe.instructions.length - 1)
            .focus();
        }, 200);
      }
    },
    async onToggleUstensil(ustensil, selected) {
      if (selected) {
        await API.recipe.addUstensil(this.recipe.id, { ustensilId: ustensil.id });
        this.recipe.ustensils.push(ustensil.id);
      } else {
        await API.recipe.removeUstensil(this.recipe.id, { ustensilId: ustensil.id });
        this.recipe.ustensils = this.recipe.ustensils.filter((id) => id != ustensil.id);
      }
    },
    async saveRecipe() {
      // Reset error message
      this.errorStatus = undefined;
      // Some checks
      if (!this.saveInstructions() || !this.checkIngredients() || !this.checkDishtype() || !this.checkName()) {
        this.recipe.status = STATUS_VALIDATED;
        return;
      }
      // Update the recipe itself (title, price, ..)
      try {
        await API.recipe.update(this.recipe.id, this.recipe);
        this.$store.dispatch("cookbook/update");
        this.$router.push({ name: "Cookbook" });
      } catch (error) {
        let status = "";
        if (error.response) {
          //  Mmmh, weird
          status = error.response.status || error.response.data["status"] || "";
        }
        this.errorStatus = "Erreur " + status;
      }
    },
    saveInstructions() {
      if (!this.recipe.instructions) {
        return true;
      }
      const instructionsToRemove = [];
      for (const instruction of this.recipe.instructions) {
        instruction.text = sentenceTypoCheck(instruction.text);
        if (!instruction.id) {
          console.log("error: recipe instruction without id", instruction);
          return false;
        }
        if (instruction.text.length > 3) {
          // Updating instruction
          API.recipeInstruction.update(instruction.id, instruction);
        } else {
          // Deleting instruction
          if (instruction.id) {
            instructionsToRemove.push(instruction.id);
            API.recipeInstruction.remove(instruction.id);
          }
        }
      }
      this.recipe.instructions = this.recipe.instructions.filter((i) => !includes(instructionsToRemove, i.id));
      return true;
    },
    checkIngredients() {
      if (this.ingredientList.length === 0) {
        this.errorStatus = "Votre recette ne comporte aucun ingrédient !";
        return false;
      }
      for (const ingredient of this.ingredientList) {
        if (ingredient.grams === 0 && ingredient.food.type !== COOKING_CONSUMER_GOODS_FOOD_TYPE_ID) {
          this.errorStatus =
            "Vous n'avez pas renseigné la quantité de <b>" + ingredient.food.name + "</b> dont votre recette a besoin.";
          return false;
        }
      }
      return true;
    },
    checkDishtype() {
      const result = this.recipe.dishTypes && this.recipe.dishTypes.length > 0;

      if (!result) {
        this.errorStatus = "Vous devez spécifier le type de plat dans les paramètres de votre recette.";
      }
      return result;
    },
    checkName() {
      const result = this.recipe.name;

      if (!result) {
        this.errorStatus = "Vous n'avez pas choisi de nom pour votre recette.";
      }
      return result;
    },
    async onSelectDishType(object) {
      let dishTypeIdToRemove = null;
      if (this.recipe.dishTypes.length > 0) {
        dishTypeIdToRemove = this.recipe.dishTypes[0];
      }
      this.recipe.dishTypes.push(object.id);
      await API.recipe.addDishType(this.recipe.id, { dishTypeId: object.id });
      if (dishTypeIdToRemove == null) {
        return;
      }
      this.removeDishType(this.recipe, dishTypeIdToRemove);
    },
    /*
     * Removes a dishType from a recipe (server + JS object)
     */
    removeDishType(recipe, dishTypeId) {
      API.recipe.removeDishType(recipe.id, { dishTypeId });
      const pos = recipe.dishTypes.indexOf(dishTypeId);
      recipe.dishTypes.splice(pos, 1);
    },
    onRemoveDishType(evt) {
      this.removeDishType(this.recipe, evt.val);
    },
    onChangeRecipeSpeciality(isLocated) {
      if (isLocated) {
        this.recipe.origin = this.defaultOrigin;
      } else {
        this.defaultOrigin = this.recipe.origin;
        this.recipe.origin = null;
      }
    },
    /*
     * Split available tags in two categories : hierarichal-ones,
     * and simple ones
     */
    classifyTags(recipeTagsTree) {
      const simpleTags = [];
      const treeTags = [];

      for (const _tag of recipeTagsTree) {
        const tag = { ..._tag, text: _tag.name };
        if (tag.children.length === 0) {
          // No children, and appears as first node -> simple
          simpleTags.push(tag);
        } else {
          treeTags.push(tag);
        }
      }
      this.simpleTags = simpleTags;
      this.treeTags = treeTags;
    },
    /*
     * Called when one tag is checked
     */
    onAddTag(tagId) {
      API.recipe.addTag(this.recipe.id, { tagId });
    },
    /*
     * Called when one tag is unchecked
     */
    onRemoveTag(tag) {
      API.recipe.removeTag(this.recipe.id, { tagId: tag.id });
    },
  },
  components: { Dialog, RecipeEditToolbar, Select2, EquipmentEditor, IngredientEditor, TreeCombo },
};
</script>

<style scoped lang="scss">
#recipe-publication-dialog {
  h2 {
    margin-top: 0px;
  }
}

#recipe-edit-page {
  h2 {
    color: $op-color-green;
    border-bottom: 1px solid $op-color-border;
  }

  #external-url {
    input {
      margin-top: 10px;
    }
  }

  .input-group,
  .form-group {
    margin: 10px 0px;
    line-height: 25px;
  }

  .recipe-edit-time-label {
    width: 100px;
    text-align: left;
  }

  .recipe-edit-instructions {
    .recipe-edit-instruction {
      clear: both;
    }

    .recipe-edit-instruction-text {
      background-color: white;
      border: solid 1px $op-color-border;
      border-radius: $op-radius-md;
      padding: 5px;
      margin-left: 10px;
      margin-right: 0px;
      margin-bottom: 0px;
      min-height: 30px;
      flex-grow: 999;
    }

    .recipe-edit-add-instruction-btn {
      padding: 10px;
      padding-top: 0;
      text-align: center;
    }
  }

  .recipe-edit-question {
    text-align: left;
    display: inline-block;
    margin-top: 10px;
    font-size: $op-font-md;
  }

  // Fix bug: defaut select2 style won't adapt to size
  .select2-choice {
    padding: 4px 0px 2px 8px;
    height: auto;
  }

  .input-group-text {
    img {
      height: 15px;
    }
  }

  .action-button {
    min-width: 125px;
    text-align: center;
  }
}
</style>

<style lang="scss">
#recipe-edit-page {
  .select2-container.select2-container--classic {
    .select2-selection--single {
      height: 35px;
      & > span {
        padding-top: 2px;
      }
    }
    .select2-selection__arrow {
      height: 33px;
    }
  }

  .input-group.d-flex {
    .select2-container {
      flex-grow: 1;
    }
  }

  .location-tree {
    @media (max-width: $bootstrap-md-min) {
      padding: 0 !important;
      margin-top: 30px !important;
    }
  }
}
</style>
