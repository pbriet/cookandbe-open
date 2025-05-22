<template>
  <div class="op-page op-cookbook-page">
    <div class="op-page-title">
      <h1>Ajouter des recettes favorites</h1>
    </div>

    <div class="op-page-content">
      <Dialog :open="recipeDetailsDialog" :closeBtn="true" :onClose="hideRecipeDetailsDialog">
        <div class="dialog-title">{{ selectedRecipe?.name }}</div>
        <div class="dialog-body">
          <RecipeViewer
            :recipeId="selectedRecipe.id"
            :showDetails="true"
            v-if="selectedRecipe"
            :showRatings="true"
            :mayRate="true"
          >
            <div class="op-vs-10" v-if="canAddRecipeInCookbook(selectedRecipe)">
              <button class="btn btn-success" @click="addToCookbook(selectedRecipe)">
                <FontAwesomeIcon :icon="['fas', 'check']" /> Ajouter au carnet
              </button>
            </div>
            <div class="added_to_cookbook op-vs-10" v-if="isRecipeInCookbook(selectedRecipe)">
              <FontAwesomeIcon :icon="['fas', 'check']" /> Ajoutée au carnet !
            </div>
          </RecipeViewer>
        </div>
      </Dialog>

      <div class="container-fluid">
        <div class="row">
          <div class="col-12 col-sm-6 col-md-4 op-vs">
            <router-link class="op-big-btn btn btn-secondary btn-block" :to="{ name: 'Cookbook' }">
              <div class="op-row">
                <div class="op-cell-icon">
                  <span class="op-icon-dlg op-cell-icon">
                    <FontAwesomeIcon :icon="['fas', 'chevron-left']" />
                  </span>
                </div>
                <div class="op-cell-icon">
                  <span class="op-icon-dlg">{{ nbInCookbook }}</span>
                </div>
                <div class="op-cell-text">recette<span v-if="nbInCookbook > 1">s</span> dans mon carnet</div>
              </div>
              <!-- op-row -->
            </router-link>
          </div>
          <!-- col-12 -->
        </div>
        <!-- row -->

        <h2>Rechercher une recette</h2>

        <RecipeSearch
          :onRecipeClick="onRecipeClick"
          :onBtnClick="addToCookbook"
          btnCaption="Ajouter au carnet"
          btnClass="success"
          :shouldDisplayBtnFcn="canAddRecipeInCookbook"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import Dialog from "@/components/interface/Dialog.vue";
import RecipeViewer from "@/components/recipe/recipe_viewer/RecipeViewer.vue";
import RecipeSearch from "@/components/recipe/RecipeSearch.vue";

/*
 * View for cookbook page
 */
export default {
  name: "CookbookSearch",
  props: [],
  data: () => ({
    selectedRecipe: null,
    recipeDetailsDialog: false,
  }),
  computed: {
    ...mapGetters({
      nbInCookbook: "cookbook/nbRecipes",
      recipeInCookbook: "cookbook/recipeInCookbook",
      recipeIsPersonal: "cookbook/recipeIsPersonal",
    }),
  },
  methods: {
    ...mapActions({
      addRecipe: "cookbook/addRecipe",
    }),
    onRecipeClick(recipe) {
      this.selectedRecipe = recipe;
      this.recipeDetailsDialog = true;
    },
    hideRecipeDetailsDialog() {
      this.recipeDetailsDialog = false;
    },
    addToCookbook(recipe) {
      this.addRecipe(recipe.id);
    },
    canAddRecipeInCookbook(recipe) {
      if (!recipe) {
        return false;
      }
      return !this.recipeInCookbook(recipe.id) && !this.recipeIsPersonal(recipe.id);
    },
    isRecipeInCookbook(recipe) {
      if (!recipe) {
        return false;
      }
      return this.recipeInCookbook(recipe.id);
    },
  },
  components: { RecipeViewer, RecipeSearch, Dialog },
};
</script>

<style scoped lang="scss"></style>
