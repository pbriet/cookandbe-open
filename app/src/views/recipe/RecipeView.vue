<template>
  <div class="d-print-none op-page" id="op-recipe-view-page">
    <div class="op-page-block op-vs d-print-none" itemscope itemtype="http://schema.org/Recipe">
      <div class="row">
        <div class="op-page-content col-12 col-md-8 op-vs-0">
          <RecipeViewer
            v-if="recipe"
            :recipeId="recipe.id"
            :showDetails="true"
            :mayRate="true"
            :showRatings="true"
            :showDishTypes="true"
            :ratio="ratio"
            class="ms-2"
          />
        </div>
        <div class="op-page-content col-12 col-md-4 op-vs-0" style="border-left: 1px solid #f1eee9">
          <!-- Recipe stats -->
          <div class="op-page-content">
            <RecipeStats v-if="recipe" :recipe="recipe" />
          </div>
        </div>
        <!-- col-12 -->
      </div>
      <!-- row -->
      <div class="row op-page-block-white">
        <div class="op-vs op-discover-more">
          <h2 class="also-discover">Découvrez aussi</h2>
          <div class="recipe-results-panel">
            <div>
              <div id="seasonal-recipes" v-if="recipe" class="row">
                <router-link
                  :to="{ name: 'RecipeView', params: { recipeKey: recipe.urlKey } }"
                  v-for="recipe in randomSeasonRecipes"
                  :key="recipe.urlKey"
                  class="col-12 col-sm-6 col-md-4"
                >
                  <RecipeImg :recipe="recipe">
                    <div class="overlay-row-void"></div>
                    <div class="overlay-row">
                      <div class="overlay-cell">
                        {{ recipe.name }}
                      </div>
                    </div>
                  </RecipeImg>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="op-discover-more row op-page-block-white op-vs" v-if="foodTags.length > 0 && recipe">
        <h2 class="also-discover">Autres recettes autour des mêmes ingrédients :</h2>
        <a
          class="col-12 col-sm-4"
          :href="`${WWW_HOST}/recettes/a-base-de/${foodTag.urlKey}`"
          v-for="foodTag in foodTags"
          :key="foodTag.urlKey"
        >
          <div class="row">
            <div class="op-block-image">
              <div class="op-block-image-overlay">
                <div class="overlay-table">
                  <div class="overlay-row-void"></div>
                  <div class="overlay-row">
                    <div class="overlay-cell">A base de {{ foodTag.name.toLowerCase() }}</div>
                  </div>
                </div>
              </div>
              <div class="op-block-image-body">
                <img :src="foodTag.photo" :title="foodTag.name" :alt="`Photo aliment : ${foodTag.name}`" />
              </div>
            </div>
            <!-- op-block-image -->
          </div>
        </a>
      </div>
      <!-- op-discover-food-tags -->
    </div>
    <!-- container -->
  </div>
  <!-- op-page -->

  <div class="d-none d-print-block">
    <!-- Recipe details -->
    <RecipeViewer
      v-if="recipe"
      :recipeId="recipe.id"
      :printMode="true"
      class="op-column"
      :showDetails="true"
      :mayRate="true"
      :showRatings="true"
      :ratio="ratio"
    />
  </div>
</template>

<script>
import $ from "jquery";
import API from "@/api.js";
import { WWW_HOST } from "@/config.js";
import { mapGetters, mapMutations } from "vuex";
import { RECIPE_META_DESC_DIFFICULTY, RECIPE_META_DESC_PRICE, RECIPE_META_DESC_SPEED } from "@/common/static.js";
import RecipeStats from "@/components/recipe/RecipeStats.vue";
import RecipeViewer from "@/components/recipe/recipe_viewer/RecipeViewer.vue";
import RecipeImg from "@/components/recipe/RecipeImg.vue";

export default {
  name: "RecipeView",
  props: [],
  data: () => ({
    randomSeasonRecipes: [],
    foodTags: [],
    recipe: null,
    WWW_HOST,
  }),
  mounted() {
    this.init(this.$route.params.recipeKey);
  },
  beforeRouteUpdate(to, _, next) {
    this.randomSeasonRecipes = [];
    this.foodTags = [];
    this.recipe = null;
    this.init(to.params.recipeKey);
    next();
  },
  computed: {
    ...mapGetters({
      diets: "diet/getDiets",
      dishTypeById: "cache/dishTypeById",
    }),
    ratio() {
      if (!this.$route.query.ratio) return null;
      return parseFloat(this.$route.query.ratio.replace(",", "."));
    },
  },
  methods: {
    ...mapMutations({
      metaSetTitle: "meta/setTitle",
      metaSetDescription: "meta/setDescription",
      metaSetKeywords: "meta/setKeywords",
      metaSetOgType: "meta/setOgType",
      metaSetOgImage: "meta/setOgImage",
    }),
    init(recipeKey) {
      Promise.all([
        this.$store.dispatch("cache/loadDishtypesIfNot"),
        this.$store.dispatch("recipe/getFromKey", recipeKey).then((recipe) => {
          this.recipe = recipe;
        }),
      ]).then(this.onRecipeLoaded);

      this.initRandomSelection();
    },
    async initRandomSelection() {
      const data = await API.recipe.randomSeasonSelection({ nb_recipes: 3, only_with_photo: false });
      this.randomSeasonRecipes = data.results;
    },
    /*
     * Scroll to element targeted by scrollto GET arg, if there is one
     */
    scrollToTarget() {
      if (!this.$route.query.scrollto) {
        return;
      }
      var obj = $("#" + this.$route.query.scrollto);
      if (!obj) {
        return;
      }
      $("body,html").animate({ scrollTop: obj.offset().top }, "slow");
    },
    onRecipeLoaded() {
      if (!this.recipe.exists) {
        this.$router.push({ name: "NoSuchPage" });
        return;
      }
      this.metaSetTitle("Recette : " + this.recipe.name);
      this.metaSetOgType("article");
      if (this.recipe.photo) {
        this.metaSetOgImage(this.recipe.photo);
      }
      const metaKeywordIngredients = [];
      const metaDescIngredients = [];
      for (const ing of this.recipe.ingredients) {
        if (ing.grams > 50) {
          metaKeywordIngredients.push(ing.name.toLowerCase());
          if (ing.name.length < 30 && metaDescIngredients.length < 3) {
            metaDescIngredients.push(ing.name.toLowerCase());
          }
        }
      }

      // Meta description
      let metaDesc = "La recette " + this.recipe.name + " est ";
      metaDesc = metaDesc + RECIPE_META_DESC_SPEED[this.recipe.speed - 1];
      metaDesc = metaDesc + ", " + RECIPE_META_DESC_PRICE[this.recipe.price - 1];
      metaDesc = metaDesc + " et " + RECIPE_META_DESC_DIFFICULTY[this.recipe.difficulty - 1];
      metaDesc = metaDesc + ", avec : " + metaDescIngredients.join(", ");
      this.metaSetDescription(metaDesc);

      let keywords = this.recipe.name + ", recette de cuisine, recette, menu, semaine, équilibre alimentaire";
      keywords = keywords + ", " + metaKeywordIngredients.join(",");
      for (const dishTypeId of this.recipe.dishTypes) {
        keywords = keywords + ", " + this.dishTypeById(dishTypeId).name;
      }
      this.metaSetKeywords(keywords);

      API.recipe.getSuggestedFoodTags(this.recipe.id).then(this.onMainFoodTagsLoaded);

      // Let some time for the page content to be loaded, then scroll
      setTimeout(this.scrollToTarget, 1000);
    },
    onMainFoodTagsLoaded(data) {
      const res = [];
      for (let i = 0; i < data.length; i++) {
        if (!data[i].canBeDisliked || !data[i].photo) {
          continue;
        }
        res.push(data[i]);
        if (res.length == 3) {
          break;
        }
      }
      this.foodTags = res;
    },
  },
  components: { RecipeStats, RecipeViewer, RecipeImg },
};
</script>

<style scoped lang="scss">
#op-recipe-view-page {
  #op-recipe-call-to-action {
    margin-bottom: 30px;
    .find-recipe-in {
      font-size: $op-font-lg;
      @media (min-width: $op-page-column-width-sm) {
        padding: 0px 50px;
      }
      a {
        font-weight: bold;
      }
    }
  }
  .overlay-cell {
    font-size: 16px;
  }
  .recipe-menus-cta {
    background-color: white;
    margin-top: 40px;
    padding: 20px 10px;
    h2 {
      display: inline;
    }
    a {
      margin-top: 5px;
    }
    p {
      padding-top: 10px;
      font-size: 16px;
      color: $op-color-text-main;
      font-family: $op-family-quicksand;
    }
  }
}

.op-discover-more {
  .op-block-image-body {
    img {
      height: 237px;
    }
  }
}

#seasonal-recipes,
.op-discover-more {
  a {
    padding: 0px 20px;
  }
}
</style>
