<template>
  <div class="op-recipe-search-input">
    <!-- Input -->
    <div class="recipe-search-panel">
      <div class="recipe-searchbar input-group">
        <span class="input-group-text">
          <FontAwesomeIcon :icon="['fas', 'search']" class="me-1" />
          <span class="d-none d-sm-inline" v-if="caption"> {{ caption }}</span>
        </span>
        <input
          class="form-control h-100"
          ref="searchbar"
          placeholder="Rechercher une recette"
          type="text"
          :value="keyword"
          @input="onChangeKeyword"
          autofocus
        />
        <span class="input-group-btn">
          <button class="btn btn-secondary" type="button" @click="resetSearch">
            <FontAwesomeIcon :icon="['fas', 'trash']" />
          </button>
        </span>
      </div>
      <div class="op-vs-5">
        <!-- <span class="col-12 col-sm-6"><CheckBox :checked="searchMode == 'user'" :onChange="toggleSearchMode" caption="Rechercher uniquement dans mes recettes" /></span>-->
        <div class="col-12 col-sm-6" v-show="searchMode != 'all' || keyword.length >= minChars">
          <div class="op-font-xs fright">Recettes trouvées : {{ nbRecipes }}</div>
        </div>
      </div>
      <div class="col-12" v-show="!hasEnoughCharacters">
        <h3 v-if="nbMissingCharacters > 1 && keyword.length > 0">
          ... encore {{ nbMissingCharacters }} lettres pour rechercher !
        </h3>
        <h3 v-if="nbMissingCharacters === 1">... encore 1 lettre pour rechercher !</h3>
      </div>
    </div>
  </div>
</template>

<script>
import API from "@/api.js";
import { mapGetters } from "vuex";
import { RECIPE_SEARCH_DEFAULT_MIN_CHARS } from "@/common/static.js";

const SEARCH_MODE_ALL = "all";
const SEARCH_MODE_USER = "user";

/*
 * Component that provides a search text input, and that handles API calls
 * It stores the result in recipes
 */
export default {
  name: "RecipeSearchInput",
  props: {
    keyword: {},
    recipes: {},
    nbRecipes: {},
    offset: {
      default: 0,
    },
    limit: {},
    searchMode: {
      default: SEARCH_MODE_ALL,
    },
    showTabs: {},
    caption: {},
    advancedRecipesOnly: {}, // Optional
    minChars: {
      default: RECIPE_SEARCH_DEFAULT_MIN_CHARS,
    }, // Optional
  },
  data: () => ({
    searchDelay: 300,
  }),
  mounted() {
    this.resetSearch(true);
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
      user: "user/get",
    }),
    hasEnoughCharacters() {
      return this.searchMode == SEARCH_MODE_USER || this.keyword.length >= this.minChars;
    },
    nbMissingCharacters() {
      return this.minChars - this.keyword.length;
    },
  },
  watch: {
    keyword() {
      this.updateSearch();
    },
  },
  methods: {
    resetSearch(firstInitialization) {
      this.clearSearch(firstInitialization);
      this.$emit("update:keyword", "");
    },
    clearSearch(firstInitialization) {
      this.$emit("update:nbRecipes", null);
      if (!firstInitialization) {
        this.$emit("update:offset", 0);
      }
      this.$emit("update:recipes", []);
      this.focus();
    },
    focus() {
      if (this.$refs.searchbar) {
        this.$refs.searchbar.focus();
      }
    },
    onChangeKeyword(event) {
      const keyword = event.target.value;
      this.$emit("update:offset", 0);
      this.$emit("update:keyword", keyword);
    },
    updateSearch() {
      if (!this.hasEnoughCharacters) {
        // Do not search in all database without enough characters
        this.clearSearch();
        return;
      }
      // Trick: a small search delay allows the interface to wait when the user is typing
      var keyword = this.keyword;
      setTimeout(() => {
        this.realtimeUpdateSearch(keyword);
      }, this.searchDelay);
    },
    async realtimeUpdateSearch(keyword) {
      if (keyword != this.keyword) {
        // The user is still typing, we delay the query to keep the server in peace
        return;
      }
      const data = await API.recipeSearch(keyword, this.generateSearchOptions());
      // Trick: if the keyword changed, the results are obsolete
      if (this.keyword == data.keyword) {
        this.$emit("update:recipes", data.results);
        this.$emit("update:nbRecipes", data.count);
      }
    },
    generateSearchOptions(forcedOptions) {
      let options = {};
      if (forcedOptions) {
        options = forcedOptions;
      }
      const defaultOptions = { offset: this.offset, limit: this.limit, details: "ingredients" };
      if (this.advancedRecipesOnly) {
        defaultOptions.advancedRecipesOnly = this.advancedRecipesOnly;
      }
      if (this.searchMode == SEARCH_MODE_USER && this.user) {
        defaultOptions.authorId = this.userId;
        if (this.keyword.length > 0) {
          defaultOptions.orderBy = "name";
        } else {
          defaultOptions.orderBy = "-creationDate";
        }
      }
      for (let optionName in defaultOptions) {
        if (options[optionName] === undefined) {
          options[optionName] = defaultOptions[optionName];
        }
      }
      return options;
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
.op-recipe-search-input {
  .recipe-search-panel {
    background-color: white;
  }

  .op-tabs + .recipe-search-panel {
    border: $op-page-content-border-width solid $op-color-border;
    padding: 15px;
  }

  .recipe-searchbar {
  }
}
</style>
