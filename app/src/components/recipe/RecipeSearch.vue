<template>
  <div class="container-fluid">
    <div class="row op-vs">
      <RecipeSearchInput
        ref="input"
        :recipes="searchParams.recipes"
        @update:recipes="searchParams.recipes = $event"
        :keyword="searchParams.keyword"
        @update:keyword="searchParams.keyword = $event"
        :nbRecipes="searchParams.nbRecipes"
        @update:nbRecipes="searchParams.nbRecipes = $event"
        :offset="searchParams.offset"
        @update:offset="searchParams.offset = $event"
        :limit="searchParams.nbRecipesPerPage"
        :searchMode="searchParams.searchMode"
        :minChars="searchParams.minChars"
        :advancedRecipesOnly="searchParams.advancedRecipesOnly"
      />
    </div>
    <div class="recipe-stats-panel container-fluid">
      <SearchPages
        :offset="searchParams.offset"
        :count="searchParams.nbRecipes"
        :resultsPerPage="searchParams.nbRecipesPerPage"
        :onChangePage="onChangeRecipePage"
        :pageBaseUrl="pageBaseUrl"
      />
    </div>
    <div class="clearfix"></div>
  </div>

  <!-- Recipe search results -->
  <RecipeList
    :recipes="searchParams.recipes"
    :onRecipeClick="onRecipeClick"
    :btnCaption="btnCaption"
    :onButtonClick="onBtnClick"
    :btnClass="btnClass"
    :displayBtnFcn="shouldDisplayBtnFcn"
  >
    <div v-if="isSearchEmpty" class="container-fluid op-vs">
      <h3>
        Aucune recette trouvée contenant "<b>{{ searchParams.keyword }}</b
        >"
      </h3>
      <p>Changez vos critères de recherche.</p>
    </div>
  </RecipeList>

  <div class="col-12">
    <SearchPages
      :offset="searchParams.offset"
      :count="searchParams.nbRecipes"
      :resultsPerPage="searchParams.nbRecipesPerPage"
      :onChangePage="onChangeRecipePage"
    />
  </div>
</template>

<script>
import SearchPages from "@/components/interface/SearchPages.vue";
import RecipeSearchInput from "@/components/recipe/RecipeSearchInput.vue";
import RecipeList from "@/components/recipe/RecipeList.vue";

const DEFAULT_SEARCH_PARAMS = {
  nbRecipesPerPage: 10,
  offset: undefined,
  keyword: "",
  nbRecipes: null,
  recipes: [],
  searchMode: "all",
};

/*
 * Component that displays a text input, the list of recipes, and the search pages.
 */
export default {
  name: "RecipeSearch",
  props: [
    "onRecipeClick",
    "btnIcon", // Optional
    "btnCaption", // Optional
    "btnClass", // Optional
    "onBtnClick", // Optional
    "pageBaseUrl", // Optional
    "withAdditionalSearchParams", // Optional
    "additionalSearchParams", // Optional
    "shouldDisplayBtnFcn", // Optional
  ],
  data() {
    let searchParams;
    if (this.withAdditionalSearchParams) {
      searchParams = { ...DEFAULT_SEARCH_PARAMS, ...this.additionalSearchParams };
    } else {
      searchParams = { ...DEFAULT_SEARCH_PARAMS };
    }
    return {
      searchParams,
    };
  },
  watch: {
    additionalSearchParams() {
      if (this.withAdditionalSearchParams) {
        this.searchParams = { ...DEFAULT_SEARCH_PARAMS, ...this.additionalSearchParams };
      }
    },
  },
  computed: {
    isSearchEmpty() {
      return this.searchParams.keyword && this.searchParams.nbRecipes === 0;
    },
  },
  methods: {
    onChangeRecipePage(page) {
      this.searchParams.offset = page.offset;
      this.$refs.input.updateSearch();
    },
  },
  components: { SearchPages, RecipeSearchInput, RecipeList },
};
</script>

<style scoped lang="scss"></style>
