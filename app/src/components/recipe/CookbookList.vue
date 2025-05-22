<template>
  <CookbookPopup
    :open="openPopup"
    :hideCookbookPopup="hideCookbookPopup"
    :recipe="selectedRecipe"
    :onDelete="update"
    :disableFavorite="true"
  />

  <div v-if="loading">
    <PleaseWait>Chargement en cours...</PleaseWait>
  </div>

  <div v-if="!loading">
    <div class="row">
      <div class="col-md-2"></div>
      <!-- for center alignment -->
      <div class="col-12 col-sm-6 col-md-4 op-vs">
        <router-link
          class="op-big-btn btn btn-block"
          :to="{ name: 'CookbookSearch' }"
          :class="cookbookIsEmpty ? 'btn-success' : 'btn-secondary'"
        >
          <div class="op-row">
            <div class="op-cell-icon">
              <span class="op-icon-dlg op-cell-icon">
                <FontAwesomeIcon :icon="['fas', 'heart']" />
              </span>
            </div>
            <div class="op-cell-text">Ajouter des recettes favorites</div>
          </div>
          <!-- op-row -->
        </router-link>
      </div>
      <!-- col-12 -->

      <div class="col-12 col-sm-6 col-md-4 op-vs">
        <a
          class="op-big-btn btn btn-block"
          @click.prevent="onAddRecipe"
          :class="cookbookIsEmpty ? 'btn-success' : 'btn-secondary'"
        >
          <div class="op-row">
            <div class="op-cell-icon">
              <span class="op-icon-dlg op-cell-icon">
                <FontAwesomeIcon :icon="['fas', 'plus']" />
              </span>
            </div>
            <div class="op-cell-text">Créer une recette perso</div>
          </div>
          <!-- op-row -->
        </a>
      </div>
      <!-- col-12 -->
    </div>
    <!-- op-row -->

    <div v-if="cookbookIsEmpty" class="row">
      <div class="col-12">
        <h2>Vous n'avez aucune recette dans votre carnet</h2>
        <div class="op-vs">
          <div class="op-font-xl op-vs-5">
            <span class="op-icon-xxl op-font-lime">
              <FontAwesomeIcon :icon="['fas', 'heart']" />
            </span>
            Ajoutez des recettes dans votre carnet
          </div>
          <div class="op-font-xl op-vs-5">
            <span class="op-icon-xxl op-font-grey-dark me-2">
              <FontAwesomeIcon :icon="['fas', 'arrow-right']" />
            </span>
            <span class="op-icon-xxl op-font-lime">
              <FontAwesomeIcon :icon="['fas', 'utensils']" />
            </span>
            Puis retrouvez-les dans vos suggestions de journées équilibrées !
            <span class="op-font-md">(Idées repas)</span>
          </div>
        </div>
        <!-- op-vs -->
      </div>
      <!-- col-12 -->
    </div>
    <!-- row -->

    <div v-show="!cookbookIsEmpty" class="row">
      <div class="col-12">
        <div class="op-info op-font-lg">Ces recettes sont placées en priorité dans vos suggestions équilibrées.</div>

        <div v-if="personalRecipes.values.length + cookbookRecipes.values.length > 10">
          <div class="recipe-search-panel">
            <div class="recipe-searchbar input-group">
              <span class="input-group-text">
                <FontAwesomeIcon :icon="['fas', 'search']" />
              </span>
              <input
                class="form-control h-100"
                placeholder="Entrez un mot-clé"
                type="text"
                v-model="keyword.value"
                autofocus
              />
              <span class="input-group-btn">
                <button class="btn btn-secondary" type="button" @click="keyword.value = ''">
                  <FontAwesomeIcon :icon="['fas', 'trash']" />
                </button>
              </span>
            </div>
          </div>
        </div>
        <!-- v-if personal_recipes -->

        <h3 v-if="personalRecipes.values.length">Mes recettes personnelles</h3>
        <RecipeList
          v-if="personalRecipes.values"
          :recipes="personalRecipes.values"
          :onRecipeClick="onRecipeClick"
          :keywordFilter="keyword.value"
          btnCaption="Supprimer"
          btnClass="danger"
          :onButtonClick="onDeletePersonalRecipe"
        />

        <h3 v-if="cookbookRecipes.values.length">Mes recettes favorites</h3>
        <RecipeList
          v-if="cookbookRecipes.values"
          :recipes="cookbookRecipes.values"
          :onRecipeClick="onRecipeClick"
          :keywordFilter="keyword.value"
          btnCaption="Supprimer"
          btnClass="danger"
          :onButtonClick="onDeleteCookbookRecipe"
        />
      </div>
      <!-- col-12 -->
    </div>
    <!-- row -->
  </div>
  <!-- v-if !loading -->
</template>

<script>
import RecipeList from "@/components/recipe/RecipeList.vue";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import { mapGetters } from "vuex";
import CookbookPopup from "@/components/recipe/CookbookPopup.vue";

export default {
  name: "CookbookList",
  props: ["openPopup", "showCookbookPopup", "hideCookbookPopup"],
  data: () => ({
    loading: true,
    selectedRecipe: null,
    keyword: { value: "" },
    cookbookRecipes: { values: [] },
    personalRecipes: { values: [] },
  }),
  mounted() {
    this.update();
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
    }),
    cookbookIsEmpty() {
      return this.cookbookRecipes.values.length + this.personalRecipes.values.length === 0;
    },
  },
  methods: {
    async update() {
      this.loading = true;
      await Promise.all([
        (async () => {
          this.cookbookRecipes = await this.$store.dispatch("cookbook/getRecipes");
        })(),
        (async () => {
          this.personalRecipes = await this.$store.dispatch("cookbook/getPersonalRecipes");
        })(),
      ]);
      this.loading = false;
    },
    onAddRecipe() {
      this.$store.dispatch("cookbook/createRecipe", { userId: this.userId });
    },
    onRecipeClick(recipe) {
      this.selectedRecipe = recipe;
      this.showCookbookPopup();
    },
    onDeleteCookbookRecipe(recipe) {
      this.$store.dispatch("cookbook/rmRecipe", recipe.id);
      this.update();
    },
    onDeletePersonalRecipe(recipe) {
      this.$store.dispatch("cookbook/rmPersonalRecipe", recipe);
      this.update();
    },
  },
  components: { RecipeList, CookbookPopup, PleaseWait },
};
</script>

<style scoped lang="scss"></style>
