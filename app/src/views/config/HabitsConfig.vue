<template>
  <div class="op-page">
    <div class="op-page-title">
      <h1>Vos repas</h1>
    </div>
    <ConfigProgression />
    <div class="op-page-content">
      <div id="planning-structure-config">
        <!-- Dish config editor popup  -->
        <Dialog id="dish-config-editor" :onClose="closeDishConfigEditor" :closeBtn="true" :open="openEditor">
          <DishConfigEditor
            v-if="selectedPopupDish"
            v-model:forcedRecipe="selectedPopupDish.forcedRecipe"
            :dishType="selectedPopupDish"
            :mealType="selectedPopupMealType"
            :onValidate="onUpdateDishValues"
          />
        </Dialog>
        <!-- !modal -->

        <div class="op-info">
          <span class="info-icon">
            <FontAwesomeIcon :icon="['fas', 'coffee']" />
          </span>
          <p>
            Indiquez quelles sont vos habitudes, et {{ APP_BRAND_NAME }} vous trouvera les recettes équilibrées les plus
            adaptées à votre profil.
          </p>
        </div>

        <div
          class="meal-type-habits"
          v-for="(mealTypeHabits, mealTypeIndex) in habits.content"
          :key="mealTypeHabits.mealType.id"
        >
          <h3 class="meal-type-title row">
            <div class="col-12 col-sm-4 col-md-3">{{ mealTypeHabits.mealType.name }}</div>
            <Select
              v-if="mealTypeHabits.habits.canBeStatic"
              :disabled="withDiabete"
              :options="options"
              :modelValue="mealTypeHabits.habits.suggest.enabled"
              @update:modelValue="(value) => onSwitchSuggest(mealTypeIndex, value)"
              selectClasses="col-12 col-sm-6 col-md-4"
              buttonClasses="btn-success"
            >
              <template v-slot:option="{ option }">
                <FontAwesomeIcon v-if="option.faIcon" :icon="option.faIcon" />
                {{ option.label }}
              </template>
            </Select>
          </h3>

          <div class="row">
            <div class="col-sm-3" v-if="mealTypeHabits.habits.suggest.enabled">
              <img
                :src="MEAL_IMAGE[mealTypeHabits.mealType.name]"
                v-if="MEAL_IMAGE[mealTypeHabits.mealType.name]"
                class="meal-type-img d-none d-sm-block"
              />
            </div>

            <div class="col-sm-9" v-if="mealTypeHabits.habits.refreshing">
              <PleaseWait />
            </div>

            <div
              class="col-sm-4 col-md-3"
              v-if="mealTypeHabits.habits.suggest.enabled && !mealTypeHabits.habits.refreshing"
            >
              <h5 class="meal-section-title">
                <span class="op-icon-xl">
                  <FontAwesomeIcon :icon="['far', 'clock']" />
                </span>
                Temps de préparation :
              </h5>
              <div
                v-for="speedOption in SPEED_OPTIONS"
                :key="speedOption.id"
                class="speed_option"
                @click="setTimeAvailable(mealTypeHabits, speedOption.id)"
              >
                <input type="radio" :value="speedOption.id" v-model="mealTypeHabits.habits.speed" />
                {{ speedOption.label }}
              </div>
            </div>

            <!-- Static dishes -->
            <div
              class="col-sm-12 custom-meal-recipe"
              v-if="!mealTypeHabits.habits.suggest.enabled && !mealTypeHabits.habits.refreshing"
            >
              <IngredientEditor
                :recipe="mealTypeHabits.habits.static.recipe"
                :hideOptions="true"
                v-model:ingredientList="mealTypeHabits.habits.static.recipe.ingredients"
              />
            </div>

            <!-- Suggested dishes -->
            <div
              class="col-sm-4 col-md-6"
              v-if="mealTypeHabits.habits.suggest.enabled && !mealTypeHabits.habits.refreshing"
            >
              <h5 class="meal-section-title">
                <span class="op-icon-xl">
                  <FontAwesomeIcon :icon="['fas', 'map-marker-alt']" />
                </span>
                Plats suggérés
              </h5>
              <div class="disabled-alert" v-if="withDiabete">
                <span>
                  <FontAwesomeIcon :icon="['fas', 'info-circle']" />
                </span>
                Le choix des plats n'est pas disponible en mode "diabète".
              </div>
              <div class="disabled-alert" v-if="glutenWarningMeal(mealTypeHabits)">
                <span>
                  <FontAwesomeIcon :icon="['fas', 'info-circle']" />
                </span>
                Le pain n'est pas encore disponible en mode "sans-gluten".
              </div>
              <ul class="dishtype_list">
                <li v-for="dishtype in mealTypeHabits.habits.suggest.dishTypes" :key="dishtype.id">
                  <div class="dishtype-choice">
                    <CheckBox
                      :checked="dishtype.enabled"
                      :disabled="withDiabete || disabledDishtype(dishtype)"
                      :caption="dishtype.forcedRecipe ? dishtype.forcedRecipe.name : dishtype.name"
                      :onChange="
                        () =>
                          toggleDishType(mealTypeHabits.mealType.id, dishtype, mealTypeHabits.habits.suggest.dishTypes)
                      "
                    />
                  </div>
                  <div
                    class="dishtype-option"
                    v-show="dishtype.canBeForced && dishtype.enabled"
                    @click="editDishConfig(mealTypeHabits.mealType, dishtype)"
                  >
                    <FontAwesomeIcon :icon="['fas', 'wrench']" />
                  </div>
                </li>
              </ul>
            </div>
          </div>
          <div class="clearfix"></div>
        </div>
        <!-- meal-type-habits -->
      </div>
    </div>
    <ConfigToolbar />
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import ConfigProgression from "@/components/config/ConfigProgression.vue";
import ConfigToolbar from "@/components/config/ConfigToolbar.vue";
import Dialog from "@/components/interface/Dialog.vue";
import CheckBox from "@/components/interface/CheckBox.vue";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import Select from "@/components/interface/Select.vue";
import DishConfigEditor from "@/components/config/DishConfigEditor.vue";
import IngredientEditor from "@/components/recipe/IngredientEditor.vue";
import { APP_BRAND_NAME } from "@/config.js";
import { HABITS_SPEED_OPTIONS } from "@/common/static.js";
import API from "@/api.js";

const STATIC_OR_SUGGEST = {
  true: { label: "Me suggérer des idées repas", value: true, faIcon: ["far", "lightbulb"] },
  false: { label: "Je mange toujours la même chose", value: false, faIcon: ["fas", "utensils"] },
};

const MEAL_IMAGE = {
  "Petit déjeuner": require("@/assets/img/breakfast.png"),
  Collation: require("@/assets/img/fruit.png"),
  Déjeuner: require("@/assets/img/lunch.png"),
  Goûter: require("@/assets/img/sweet_snack.png"),
  Dîner: require("@/assets/img/dinner.png"),
};

/*
 * View for displaying profiles related to current user
 */
export default {
  name: "HabitsConfig",
  props: [],
  data: () => ({
    habits: [],
    openEditor: false,
    selectedPopupDish: null,
    selectedPopupMealType: null,
    APP_BRAND_NAME,
    STATIC_OR_SUGGEST,
    MEAL_IMAGE,
    SPEED_OPTIONS: HABITS_SPEED_OPTIONS,
  }),
  mounted() {
    this.reloadHabits();
  },
  computed: {
    ...mapGetters({
      user: "user/get",
      userId: "user/id",
      isExcludedDishtype: "diet/isExcludedDishtype",
    }),
    withDiabete() {
      return this.user.objective.key === "diabete";
    },
    withGluten() {
      return this.user.objective.key === "gluten_free";
    },
    options() {
      return Object.values(STATIC_OR_SUGGEST);
    },
  },
  methods: {
    onSwitchSuggest(index, value) {
      const mealTypeHabits = this.habits.content[index];
      this.setMealtypeSuggest(mealTypeHabits, value);
    },
    /*
     * Select / deselect a dish type in a meal
     */
    toggleDishType(mealTypeId, dishtypeValues, allDishTypes) {
      if (!dishtypeValues.enabled) {
        dishtypeValues.enabled = true;
        // Check
        API.userHabits.enableMealDish(this.userId, mealTypeId, { dishTypeId: dishtypeValues.id });
        return;
      }
      // Uncheck
      // If there is just one element remaining : refuse
      let nbChecked = 0;
      for (let i = 0; i < allDishTypes.length; i++) {
        if (allDishTypes[i].enabled) {
          nbChecked += 1;
        }
      }
      if (nbChecked == 1) {
        return; // Forbidden : there must be at least one element
      }
      dishtypeValues.enabled = false;
      API.userHabits.disableMealDish(this.userId, mealTypeId, { dishTypeId: dishtypeValues.id });
    },
    setMealtypeSuggest(mealTypeHabits, suggest) {
      if (mealTypeHabits.habits.suggest.enabled == suggest) {
        return;
      }
      mealTypeHabits.habits.refreshing = true;
      API.userHabits.setSuggest(this.userId, mealTypeHabits.mealType.id, { suggest }).then(() => {
        this.reloadHabits(mealTypeHabits.mealType.id);
      });
    },
    /*
     * Reload the user default planning
     */
    async reloadHabits(mealTypeId) {
      if (!mealTypeId) {
        // Reloading everything
        this.habits = await API.userHabits.get(this.userId);
        this.onHabitsReloaded();
        return;
      }
      // Reloading one mealType only
      const data = await API.userHabits.mealTypeHabits(this.userId, mealTypeId);
      for (let i = 0; i < this.habits.content.length; i++) {
        if (this.habits.content[i].mealType.id == mealTypeId) {
          this.habits.content[i].habits = data;
          this.onMealHabitReloaded(data);
          return;
        }
      }
    },
    onHabitsReloaded() {
      for (let i = 0; i < this.habits.content.length; ++i) {
        this.onMealHabitReloaded(this.habits.content[i].habits);
      }
    },
    onMealHabitReloaded(mealHabit) {
      if (!mealHabit.canBeStatic) {
        return;
      }

      this.$store.commit("recipe/clearCached", mealHabit.static.recipe.id);
    },
    editDishConfig(mealType, dishType) {
      this.selectedPopupDish = dishType;
      this.selectedPopupMealType = mealType;
      this.openEditor = true;
    },
    closeDishConfigEditor() {
      this.openEditor = false;
    },
    /*
     * Handle the return of the dish config edit popup
     */
    onUpdateDishValues(mealType, dishType) {
      this.closeDishConfigEditor();

      let forcedRecipeId;
      // Retrieving the new values for this meal_type/dish
      if (!dishType.forcedRecipe) {
        forcedRecipeId = -1; // Deleting forced recipe
      } else {
        forcedRecipeId = dishType.forcedRecipe.id;
      }

      // Update server-side
      API.userHabits.forceRecipe(this.userId, mealType.id, {
        dishTypeId: dishType.id,
        forcedRecipeId: forcedRecipeId,
      });
    },
    /*
     * When the user changes the "speed" of the meal
     */
    setTimeAvailable(mealTypeHabits, speed) {
      const mealTypeId = mealTypeHabits.mealType.id;
      mealTypeHabits.habits.speed = speed;
      // Update server-side
      API.userHabits.setMealSpeed(this.userId, mealTypeId, { value: speed });
    },
    glutenWarningMeal(mealTypeHabits) {
      if (!this.withGluten) {
        return false;
      }
      for (let dt = 0; dt < mealTypeHabits.habits.suggest.dishTypes.length; ++dt) {
        const dishtype = mealTypeHabits.habits.suggest.dishTypes[dt];
        if (this.disabledDishtype(dishtype)) {
          return true;
        }
      }
      return false;
    },
    disabledDishtype(dishtype) {
      return this.isExcludedDishtype(dishtype.name);
    },
    checkIngredients() {
      const incompleteIngredients = [];

      for (let i = 0; i < this.habits.content.length; i++) {
        const meal = this.habits.content[i];

        if (meal.habits.static.recipe) {
          for (let j = 0; j < meal.habits.static.recipe.ingredients.length; ++j) {
            const ingredient = meal.habits.static.recipe.ingredients[j];

            if (ingredient.grams <= 0) {
              incompleteIngredients.push(ingredient.food.name);
            }
          }
        }
      }
      if (incompleteIngredients.length === 0) {
        return true;
      }
      window.alert(
        "Les quantités des ingrédients suivants n'ont pas été renseignées:\n- " + incompleteIngredients.join("\n- ")
      );
      return false;
    },
    save() {
      if (!this.checkIngredients()) {
        return false;
      }
      this.$store.dispatch("configStage/complete", { stageName: "habits", modifyMetaplanning: true });
      return true;
    },
  },
  beforeRouteLeave(to, from, next) {
    if (this.save()) {
      next();
    }
  },
  components: {
    ConfigProgression,
    ConfigToolbar,
    Dialog,
    PleaseWait,
    DishConfigEditor,
    IngredientEditor,
    CheckBox,
    Select,
  },
};
</script>

<style lang="scss">
#planning-structure-config {
  .disabled-alert {
    color: $op-color-alert-danger;
  }

  .meal-type-title {
    border-bottom: $op-page-content-border-width solid $op-color-border;
    .selectpicker {
      border-bottom: none;
      border-radius: 0px;
    }
  }

  li {
    list-style-type: none;
  }

  .dishtype_list {
    margin-bottom: 20px;
    margin-top: 10px;
    padding-left: 15px;

    li > div {
      vertical-align: top;
      display: inline-block;
    }
  }

  .meal-type-habits {
    padding-bottom: 10px;

    .meal-type-img {
      max-width: 200px;
    }
  }

  .custom-meal-recipe {
    padding: 10px;
  }

  .bordered_row {
    border: 1px solid $op-color-border;
    border-top: none;

    &:after {
      @extend .clearfix;
    }
  }

  .dishtype-choice {
    width: 150px;
  }

  .dishtype-option:hover {
    cursor: pointer;
  }

  .meal-section-title {
    margin-top: 0.5rem;
    font-weight: bold;
  }

  .speed_option {
    cursor: pointer;
    padding-left: 20px;
    max-width: 200px;

    &:hover {
      background-color: $op-color-grey-dark;
      color: white;
    }
  }

  .action {
    font-weight: bold;
    margin-left: 10px;
    margin-top: 5px;
  }
}
</style>
