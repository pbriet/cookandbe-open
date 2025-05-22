<template>
  <div class="op-page op-cookbook-page">
    <div class="op-page-title">
      <h1>Les recettes de mon carnet</h1>
    </div>

    <TabMenu :elements="tabmenuElements" :selectedTab="selectedTab" :onTabClick="onTabClick" />

    <div class="op-page-content">
      <div v-if="selectedTab === 'all_recipes'">
        <CookbookPopup :open="cookbookPopup" :hideCookbookPopup="hideCookbookPopup" :recipe="allRecipesSelected" />
        <RecipeSearch :onRecipeClick="onAllRecipesClick" />
      </div>

      <CookbookList
        :openPopup="cookbookPopup"
        :showCookbookPopup="showCookbookPopup"
        :hideCookbookPopup="hideCookbookPopup"
        v-if="selectedTab === 'cookbook'"
      />
    </div>
  </div>
</template>

<script>
import TabMenu from "@/components/interface/TabMenu.vue";
import CookbookPopup from "@/components/recipe/CookbookPopup.vue";
import CookbookList from "@/components/recipe/CookbookList.vue";
import RecipeSearch from "@/components/recipe/RecipeSearch.vue";

export default {
  name: "Cookbook",
  props: [],
  data() {
    return {
      cookbookPopup: false,
      allRecipesSelected: null,
      tabmenuElements: [
        { caption: "Mon carnet", key: "cookbook" },
        { caption: "Toutes les recettes", key: "all_recipes" },
      ],
      selectedTab: this.$route.params.tab || "cookbook",
    };
  },
  beforeRouteUpdate(to, _, next) {
    if (this.selectedTab == (to.params.tab || "cookbook")) {
      // tab did not actually changed, do nothing
      next(false);
      return;
    }
    this.selectedTab = to.params.tab || "cookbook";
    this.allRecipesSelected = null;
    this.cookbookPopup = false;
    next();
  },
  computed: {},
  methods: {
    /*
     * Redirect on sub url, to make the return button works correctly (staying at same tab)
     */
    onTabClick(tab) {
      this.$router.push({ name: "Cookbook", params: { tab } });
    },
    /*
     * Search in all recipes : redirect to recipe page
     */
    onAllRecipesClick(recipe) {
      this.allRecipesSelected = recipe;
      this.showCookbookPopup();
    },
    showCookbookPopup() {
      this.cookbookPopup = true;
    },
    hideCookbookPopup() {
      this.cookbookPopup = false;
    },
  },
  components: { TabMenu, CookbookPopup, RecipeSearch, CookbookList },
};
</script>

<style lang="scss">
.op-cookbook-page {
  .modal-dialog {
    @media (min-width: $bootstrap-md-min) {
      min-width: 900px;
    }
    .added_to_cookbook {
      font-size: $op-font-xxl;
      color: $op-color-lime;
    }
  }
}
</style>
