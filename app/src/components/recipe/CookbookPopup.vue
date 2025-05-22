<template>
  <Dialog :open="open" :closeBtn="true" :onClose="hideCookbookPopup">
    <div class="dialog-title">{{ recipe?.name }}</div>
    <div class="dialog-body">
      <RecipeViewer
        :recipeId="recipe.id"
        :showDetails="true"
        :withTitle="false"
        v-if="recipe"
        :disableFavorite="disableFavorite"
        :showRatings="true"
        :mayRate="true"
      >
        <div class="op-vs-10">
          <button class="btn btn-danger" v-if="inCookbook && !canEdit" @click="onDeleteCookbookRecipe">
            <FontAwesomeIcon :icon="['fas', 'times']" /> Supprimer du carnet
          </button>
          <button class="btn btn-success me-1" v-if="canEdit" @click="editPersonalRecipe">
            <FontAwesomeIcon :icon="['fas', 'pencil-alt']" /> Modifier
          </button>
          <button class="btn btn-danger" v-if="canEdit" @click="onDeletePersonalRecipe">
            <FontAwesomeIcon :icon="['fas', 'times']" /> Supprimer cette recette
          </button>
        </div>
      </RecipeViewer>
    </div>
  </Dialog>
</template>

<script>
import Dialog from "@/components/interface/Dialog.vue";
import RecipeViewer from "@/components/recipe/recipe_viewer/RecipeViewer.vue";
import { recipeEditPath } from "@/common/path.js";
import { mapGetters } from "vuex";

export default {
  name: "CookbookPopup",
  props: ["open", "recipe", "onDelete", "disableFavorite", "hideCookbookPopup"],
  data: () => ({}),
  computed: {
    ...mapGetters({
      user: "user/get",
    }),
    canEdit() {
      return this.$store.getters["recipe/canEdit"](this.user, this.recipe);
    },
    inCookbook() {
      return this.$store.getters["cookbook/recipeInCookbook"](this.recipe.id);
    },
  },
  methods: {
    onDeleteCookbookRecipe() {
      this.$store.dispatch("cookbook/rmRecipe", this.recipe.id);
      this.onDelete && this.onDelete();
    },
    editPersonalRecipe() {
      this.$router.push(recipeEditPath(this.recipe));
    },
    onDeletePersonalRecipe() {
      this.$store.dispatch("cookbook/rmPersonalRecipe", this.recipe);
      this.hideCookbookPopup();
      this.onDelete && this.onDelete();
    },
  },
  components: { RecipeViewer, Dialog },
};
</script>

<style scoped lang="scss"></style>
