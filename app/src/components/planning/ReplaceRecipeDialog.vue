<template>
  <Dialog
    id="day-planner-replace-search"
    maxWidth="900px"
    :closeBtn="true"
    :open="open"
    :onClose="hideReplacePopup"
    focusElt="input"
  >
    <div class="dialog-title">Choisissez une recette</div>
    <!-- Replace search area -->
    <div class="dialog-body">
      <div class="row">
        <div class="col-12">
          <RecipeSearchInput
            v-if="open"
            ref="input"
            :recipes="search.recipes"
            @update:recipes="updateSearch({ recipes: $event })"
            :keyword="search.keyword"
            @update:keyword="updateSearch({ keyword: $event })"
            :nbRecipes="search.nbRecipes"
            @update:nbRecipes="updateSearch({ nbRecipes: $event })"
            :offset="search.offset"
            @update:offset="updateSearch({ offset: $event })"
            :limit="search.limit"
            :searchMode="search.mode"
            caption="Remplacer par"
          />
        </div>
        <div class="col-12" style="text-align: center">
          <SearchPages
            :offset="search.offset"
            :count="search.nbRecipes"
            :resultsPerPage="search.limit"
            :onChangePage="onChangeSearchPage"
          />
        </div>

        <div class="clearfix"></div>

        <RecipeList
          :recipes="search.recipes"
          :onButtonClick="onChangeRecipe"
          btnCaption="Sélectionner"
          btnClass="success"
        >
          <div v-if="search.nbRecipes === 0 && search.keyword" class="container-fluid op-vs">
            <h3>
              Aucune recette trouvée contenant "<b>{{ search.keyword }}</b
              >"
            </h3>
            <p>
              Changez vos critères de recherche ou ajoutez vos propres recettes, nous calculerons leurs apports
              nutritionnels !
            </p>
            <span class="col-12 text-center op-vs">
              <button class="btn btn-success" @click="onAddRecipe">Ajouter une recette</button>
            </span>
          </div>
        </RecipeList>
        <div class="col-12" style="text-align: center">
          <SearchPages
            :offset="search.offset"
            :count="search.nbRecipes"
            :resultsPerPage="search.limit"
            :onChangePage="onChangeSearchPage"
          />
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script>
import Dialog from "@/components/interface/Dialog.vue";
import SearchPages from "@/components/interface/SearchPages.vue";
import RecipeSearchInput from "@/components/recipe/RecipeSearchInput.vue";
import RecipeList from "@/components/recipe/RecipeList.vue";

export default {
  name: "ReplaceRecipeDialog",
  props: ["open", "hideReplacePopup", "search", "onChangeRecipe", "onAddRecipe"],
  data: () => ({}),
  computed: {},
  methods: {
    updateSearch(fields) {
      this.$emit("update:search", Object.assign(this.search, fields));
    },
    onChangeSearchPage(page) {
      this.updateSearch({ offset: page.offset });
      this.$nextTick(() => {
        this.$refs.input.updateSearch();
      });
    },
  },
  components: { SearchPages, RecipeSearchInput, RecipeList, Dialog },
};
</script>

<style scoped lang="scss"></style>
