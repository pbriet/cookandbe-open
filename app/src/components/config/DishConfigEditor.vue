<template>
  <h3 class="dialog-title">{{ mealType.name }} &gt; {{ dishType.name }}</h3>

  <div class="dialog-body">
    <p>Souhaitez-vous que {{ APP_BRAND_NAME }} choisisse le meilleur plat à votre place ?</p>

    <div id="dish-config-editor-choice">
      <ul>
        <li>
          <input type="radio" name="dish-config-radio" value="auto" @change="updateModel" v-model="recipeGeneration" />
          Oui, laisser {{ APP_BRAND_NAME }} choisir pour moi
        </li>
        <li>
          <input
            type="radio"
            name="dish-config-radio"
            value="forced"
            @change="updateModel"
            v-model="recipeGeneration"
          />
          Non, je prends toujours :
          <select :value="selectedRecipe" @change="onSelectRecipe">
            <option v-for="recipe in recipeValues" :value="recipe.id" :key="recipe.id">{{ recipe.name }}</option>
          </select>
        </li>
      </ul>
    </div>

    <button id="ok-button" class="btn btn-success" @click="apply">Appliquer la configuration</button>
  </div>
</template>

<script>
import { APP_BRAND_NAME } from "@/config.js";
import API from "@/api.js";

/*
 * This component adds a panel to edit dish configuration
 */
export default {
  name: "DishConfigEditor",
  props: ["forcedRecipe", "mealType", "dishType", "onValidate"],
  data() {
    return {
      recipeValues: null,
      recipeGeneration: null,
      selectedRecipe: this.forcedRecipe?.id,
      APP_BRAND_NAME,
    };
  },
  computed: {},
  mounted() {
    this.reset();
  },
  watch: {
    dishType() {
      this.reset();
    },
  },
  methods: {
    async reset() {
      if (!this.dishType) {
        return;
      }
      /*
       * Retrieve the available recipes for this dish type
       */
      this.recipeValues = await API.recipes({ dish_type_id: this.dishType.id, status: "published" });
      if (this.forcedRecipe) {
        this.recipeGeneration = "forced";
        this.selectedRecipe = this.forcedRecipe.id;
      } else {
        this.recipeGeneration = "auto";
        this.selectedRecipe = this.recipeValues[0].id;
      }
    },
    // When selecting a recipe, automatically pass in "forced recipe mode",
    // event if it wasn't
    onSelectRecipe(event) {
      const selectedRecipe = event.target.value;
      this.recipeGeneration = "forced";
      const forcedRecipe = this.recipeValues.filter((recipe) => recipe.id == selectedRecipe)[0];
      this.$emit("update:forcedRecipe", forcedRecipe);
    },
    updateModel() {
      // Todo: be able to set a food tag / a recipe tag
      const forcedRecipe =
        this.recipeGeneration == "forced"
          ? this.recipeValues.filter((recipe) => recipe.id == this.selectedRecipe)[0]
          : null;
      this.$emit("update:forcedRecipe", forcedRecipe);
    },
    /*
     * When the user clicks on "apply"
     */
    apply() {
      // Report the modification
      this.onValidate(this.mealType, this.dishType);
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
ul {
  li {
    list-style-type: none;
    select {
      margin-top: 10px;
      margin-left: 20px;
      display: inline-block;
      width: 200px;
    }
  }
}

#ok-button {
  margin-top: 20px;
  margin-left: 20px;
}
</style>
