<template>
  <div class="op-recipe-list-panel">
    <div class="op-empty-list-panel" v-show="!recipes || recipes.length == 0">
      <slot></slot>
    </div>
    <div
      v-for="(recipe, index) in filteredRecipes"
      :key="recipe.id"
      class="recipe-item"
      :class="{ clickable: onRecipeClick }"
    >
      <router-link :to="recipeLink(recipe)" @[onRecipeClickEvent]="recipeClick(recipe)">
        <div v-if="index >= 20">{{ recipe.name }}</div>
        <div class="recipe-table" v-if="index < 20">
          <div class="recipe-row-sm">
            <div class="recipe-row-xs recipe-cell-sm">
              <div class="recipe-cell-xs op-vs-10 op-hs-10" @click="recipeClick(recipe)">
                <RecipeImg :recipe="recipe" :disc="true" />
              </div>
            </div>
            <div class="recipe-row-xs recipe-cell-sm op-recipe-item-panel" @click="recipeClick(recipe)">
              <div class="recipe-cell-xs">
                <h3 class="recipe-title col-sm-12">
                  {{ recipe.name }}
                  <span class="d-none d-sm-inline op-font-lg fright">
                    <RatingStars :value="recipe.avgRating" />
                  </span>
                </h3>
                <span class="d-sm-none op-font-lg xs-stars">
                  <RatingStars :value="recipe.avgRating" v-if="recipe.avgRating" />
                </span>
                <div class="recipe-tag">
                  <img class="recipe-icon" src="@/assets/img/recipe/toque.png" /> {{ getDifficulty(recipe) }}
                </div>
                <div class="recipe-tag">
                  <img class="recipe-icon" src="@/assets/img/recipe/time.png" /> {{ getSpeed(recipe) }}
                </div>
                <div class="recipe-tag">
                  <img class="recipe-icon" src="@/assets/img/recipe/cost.png" /> {{ getCost(recipe) }}
                </div>
                <div class="recipe-tag">
                  <img class="recipe-icon" src="@/assets/img/recipe/people.png" /> {{ recipe.nbPeople }}
                </div>
                <div class="recipe-extract recipe-hidden-xs recipe-hidden-sm">
                  <b>Ingrédients:</b> {{ getIngredientList(recipe) }}.
                </div>
                <!-- <div class="recipe-extract"><b>Instructions:</b> {{ getInstructionList(recipe) }}</div> -->
              </div>
            </div>
            <div class="recipe-row-xs recipe-cell-sm action-cell recipe-button" v-if="showButton(recipe)">
              <div :class="`btn btn-${btnClass} text-nowrap`" @click.prevent.stop="onButtonClick(recipe)">
                {{ btnCaption }}
              </div>
            </div>
          </div>
        </div>
        <div class="recipe-hidden-md">
          <div class="recipe-extract" style="padding: 10px"><b>Ingrédients:</b> {{ getIngredientList(recipe) }}.</div>
          <!-- <div class="recipe-extract"><b>Instructions:</b> {{ getInstructionList(recipe) }}</div> -->
        </div>
      </router-link>
    </div>
  </div>
</template>

<script>
import RecipeImg from "@/components/recipe/RecipeImg.vue";
import RatingStars from "@/components/interface/RatingStars.vue";
import { find, includes, some } from "lodash";
import {
  RECIPE_PRICE_OPTIONS,
  RECIPE_SPEED_OPTIONS,
  RECIPE_DIFFICULTY_OPTIONS,
  DEFAULT_RECIPE_INSTRUCTION,
} from "@/common/static.js";

export default {
  name: "RecipeList",
  props: [
    "recipes",
    "onRecipeClick",
    "hrefMode", // If true, will use the href="" links of the recipes, and no call to onRecipeClick
    "onButtonClick",
    "keywordFilter", // keyword filter
    "btnCaption",
    "btnClass",
    "displayBtnFcn", // Optional, if defined, will display a button only if the function returns true
  ],
  data: () => ({}),
  computed: {
    onRecipeClickEvent() {
      return !this.hrefMode ? "click.prevent.stop" : null;
    },
    recipeClick() {
      return !this.onRecipeClick ? () => {} : this.onRecipeClick;
    },
    filteredRecipes() {
      let recipes = this.recipes;
      if (this.keywordFilter) {
        recipes = recipes.filter(
          (recipe) =>
            includes(recipe.name.toLowerCase(), this.keywordFilter.toLowerCase()) ||
            some(recipe.ingredients, (ingredient) =>
              includes(ingredient.name.toLowerCase(), this.keywordFilter.toLowerCase())
            ) ||
            some(recipe.instructions, (instruction) =>
              includes(instruction.text.toLowerCase(), this.keywordFilter.toLowerCase())
            )
        );
      }
      return recipes;
    },
  },
  methods: {
    recipeLink(recipe) {
      return this.hrefMode ? { name: "RecipeView", params: { recipeKey: recipe.urlKey } } : "";
    },
    getDifficulty(recipe) {
      if (!recipe.difficulty) {
        return "";
      }
      return find(RECIPE_DIFFICULTY_OPTIONS, ["id", recipe.difficulty]).label;
    },
    getCost(recipe) {
      if (!recipe.price) {
        return "";
      }
      return find(RECIPE_PRICE_OPTIONS, ["id", recipe.price]).label;
    },
    getSpeed(recipe) {
      if (!recipe.speed) {
        return "";
      }
      return find(RECIPE_SPEED_OPTIONS, ["id", recipe.speed]).label;
    },
    getIngredientList(recipe) {
      let res = "";
      for (let i = 0; i < recipe.ingredients.length; ++i) {
        if (res.length) {
          res += ", ";
        }
        res += recipe.ingredients[i].food.name;
      }
      if (!res.length) {
        res = "aucun";
      }
      return res.toLowerCase();
    },
    getInstructionList(recipe) {
      let res = "";
      for (let i = 0; i < recipe.instructions.length; ++i) {
        if (res.length) {
          res += " ";
        }
        res += recipe.instructions[i].text;
      }
      if (!res.length) {
        res = DEFAULT_RECIPE_INSTRUCTION;
      }
      return res;
    },
    /*
     * Returns true if a button should be displayed
     */
    showButton(recipe) {
      if (!this.btnCaption) {
        return false;
      }
      if (this.displayBtnFcn) {
        return this.displayBtnFcn(recipe);
      }
      return true;
    },
  },
  components: { RecipeImg, RatingStars },
};
</script>

<style scoped lang="scss">
.op-recipe-list-panel {
  text-align: center;

  .op-empty-list-panel {
    font-weight: bold;
  }

  a {
    color: inherit;
    text-decoration: inherit;
  }

  .recipe-table {
    display: table;
    width: 100%;
  }

  .recipe-item {
    &:after {
      @extend .clearfix;
    }
  }

  .recipe-item.clickable {
    &:hover {
      cursor: pointer;
      background-color: $op-color-green-light;
    }
  }

  .recipe-item:nth-child(even) {
    @include op-table-row-even;
  }
  .recipe-item:nth-child(odd) {
    @include op-table-row-odd;
  }

  @media (max-width: $bootstrap-xs-max) {
    .recipe-row-xs {
      display: table-row;
    }
    .recipe-cell-xs {
      display: table-cell;
      vertical-align: top;
    }
    .recipe-hidden-xs {
      display: none;
    }
  }
  @media (min-width: $bootstrap-sm-min) and (max-width: $bootstrap-sm-max) {
    .recipe-row-sm {
      display: table-row;
    }
    .recipe-cell-sm {
      display: table-cell;
      vertical-align: top;
    }
    .recipe-hidden-sm {
      display: none;
    }
  }
  @media (min-width: $bootstrap-md-min) {
    .recipe-row-sm {
      display: table-row;
    }
    .recipe-cell-sm {
      display: table-cell;
      vertical-align: top;
    }
    .recipe-hidden-md {
      display: none;
    }
  }

  .op-block-image {
    @media (max-width: $bootstrap-xs-max) {
      width: 200px;
      width: 200px;
    }
    @media (min-width: $bootstrap-sm-min) {
      width: 110px;
      height: 110px;
    }
  }

  .op-recipe-item-panel {
    display: block;
    padding: 10px;
    text-align: left;
    /*         width: 100%; */

    overflow: hidden;
    -o-text-overflow: ellipsis; /* pour Opera 9 */
    text-overflow: ellipsis; /* pour le reste du monde */

    $tag_height: 20px;

    .recipe-tag {
      float: left;
      width: 140px;
      height: $tag_height;
      padding-left: 5px;
      display: inline-block;
    }

    .recipe-button {
      height: $tag_height * 2;
      float: right;
    }

    .recipe-title {
      padding-left: 0px;
      margin-top: 5px;
      overflow: hidden;
      -o-text-overflow: ellipsis; /* pour Opera 9 */
      text-overflow: ellipsis; /* pour le reste du monde */
    }

    .xs-stars {
      margin-bottom: 5px;
    }

    .recipe-icon {
      height: 20px;
    }
  }
  .action-cell {
    vertical-align: middle;
    padding-right: 10px;
  }

  .recipe-extract {
    text-align: left;
    width: 100%;
    float: left;
    padding-top: 5px;
    font-size: 9pt;
  }
}
</style>
