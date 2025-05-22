<template>
  <div class="recipe-viewer-content">
    <!-- itemscope / itemtype : Google structured data -->
    <div class="d-print-none" v-if="recipeData && !printMode">
      <!-- Title -->
      <div class="row" v-if="withTitle ?? true">
        <div class="col-12">
          <Favorite
            v-if="!disableFavorite && recipeData"
            :toggleFavorite="toggleFavorite"
            :recipeDataId="recipeData.id"
            :isCustomRecipe="isCustomRecipe"
            :isPersonal="isPersonal"
            :inCookbook="inCookbook"
          />
          <ConditionalH1 :when="!printMode">
            <span itemprop="name">{{ recipeData.name }}</span>
          </ConditionalH1>
          <small class="recipe-viewer-dishtypes" itemprop="recipeCategory" v-if="showDishTypes">
            {{ getDishTypes }}
          </small>
        </div>
      </div>

      <div class="row">
        <!-- Image -->
        <div class="col-12 col-sm-8 col-lg-6 op-vs-10">
          <RecipeImg :recipe="recipeData" :title="recipeData.name" :hideIcons="true">
            <div class="overlay-row" v-if="mayUpload">
              <UploadButton
                class="overlay-cell-void image-upload"
                :onUpload="onUpload"
                text="Envoyer une image"
                :showPleaseWait="uploadInProgress"
              />
            </div>
          </RecipeImg>
        </div>
        <span class="clearfix d-sm-none" />

        <!-- Tags -->
        <div v-if="showDetails && recipeData && !recipeData.internal" class="col-12 col-sm-4 col-lg-6">
          <InfosTag
            :recipeData="recipeData"
            :canEditRecipe="canEditRecipe"
            :extractHostname="extractHostname"
            :displayPrint="displayPrint"
            :ratio="ratio"
            :fullUrl="fullUrl"
          />
        </div>
      </div>

      <div class="row">
        <div class="col-12">
          <div class="recipe-transclusion">
            <slot></slot>
          </div>
        </div>

        <!-- Warnings -->
        <RecipeWarnings :recipeWarnings="recipeWarnings" />
      </div>

      <div class="row recipe-details">
        <!-- Ingredients -->
        <div class="recipe-details-block" v-if="showDetails && recipeData">
          <Ingredients
            :eaterIds="eaterIds"
            :ratio="ratio"
            :nbPeople="recipeData.nbPeople"
            :ingredients="recipeData.ingredients"
            :printMode="printMode"
          />
        </div>

        <!-- Instructions -->
        <div class="recipe-details-block op-vs-10" v-if="showDetails && recipeData">
          <Instructions :printMode="printMode" :instructions="recipeData.instructions" />
        </div>

        <!-- Add rating -->
        <div class="recipe-details-block" v-if="mayRate && !isUserAuthor">
          <AddRating
            :rating="rating"
            v-model:comment="rating.comment"
            v-model:mouseover="rating.mouseover"
            :setRating="setRating"
            :rateRecipe="rateRecipe"
            :printMode="printMode"
          />
        </div>

        <!-- Ratings -->
        <div class="recipe-details-block" v-if="showRatings">
          <Ratings
            v-if="recipeRatings"
            :recipeRatings="recipeRatings"
            :ratingsPage="ratingsPage"
            :onChangeRatingsPage="onChangeRatingsPage"
            :printMode="printMode"
          />
        </div>
      </div>

      <div class="clearfix"></div>
    </div>

    <!-- Print mode -->
    <div class="d-none d-print-block" v-if="printMode && recipeData">
      <RecipePrint
        :recipeData="recipeData"
        :showDetails="showDetails"
        :ratio="ratio"
        :eaterIds="eaterIds"
        :getDishTypes="getDishTypes"
        :extractHostname="extractHostname"
        :canEditRecipe="canEditRecipe"
      />
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import API from "@/api.js";
import ConditionalH1 from "@/components/interface/conditional_headers/ConditionalH1.vue";
import UploadButton from "@/components/interface/UploadButton.vue";
import Favorite from "@/components/recipe/recipe_viewer/Favorite.vue";
import RecipeImg from "@/components/recipe/RecipeImg.vue";
import InfosTag from "@/components/recipe/recipe_viewer/InfosTag.vue";
import RecipeWarnings from "@/components/recipe/recipe_viewer/RecipeWarnings.vue";
import Ingredients from "@/components/recipe/recipe_viewer/Ingredients.vue";
import Instructions from "@/components/recipe/recipe_viewer/Instructions.vue";
import AddRating from "@/components/recipe/recipe_viewer/AddRating.vue";
import Ratings from "@/components/recipe/recipe_viewer/Ratings.vue";
import RecipePrint from "@/components/recipe/recipe_viewer/RecipePrint.vue";
import { opParseUrl } from "@/common/url.js";
import { recipePath } from "@/common/path.js";

/*
 * This component displays a recipe with the correct ratio
 */
export default {
  name: "RecipeViewer",
  props: [
    "recipeId",
    "recipe",
    "printMode",
    "disableFavorite",
    "withTitle",
    "showDishTypes",
    "showRatings",
    "showDetails",
    "ratio",
    "mayRate",
    "mayUpload",
    "eaterIds",
  ],
  data: () => ({
    recipeData: null,
    ratingsPage: null,
    recipeRatings: null,
    rating: {},
    fullUrl: null,
    isPersonal: false,
    inCookbook: false,
    toggleFavoriteInProgress: false,
    uploadInProgress: false,
  }),
  mounted() {
    this.reset({ recipe: this.recipe, recipeId: this.recipeId });
  },
  watch: {
    recipeId(newRecipeId) {
      this.reset({ recipeId: newRecipeId });
    },
    recipe(newRecipe) {
      this.reset({ recipe: newRecipe });
    },
  },
  computed: {
    ...mapGetters({
      user: "user/get",
      userId: "user/id",
      isLoggedIn: "user/isLoggedIn",
      getWarnings: "recipeFilter/getWarnings",
    }),
    isCustomRecipe() {
      if (!this.recipeData) {
        return null;
      }
      return this.getDishTypes == "Personnalisé";
    },
    getDishTypes() {
      if (!this.recipeData || !this.recipeData.dishTypes) {
        return "";
      }
      const cachedValues = this.$store.getters["cache/getDishTypes"](this.recipeData.dishTypes, "name");
      if (!cachedValues) {
        return "";
      }
      return cachedValues.join(" - ");
    },
    isUserAuthor() {
      return this.userId === this.recipeData.author;
    },
    canEditRecipe() {
      return this.$store.getters["recipe/canEdit"](this.user, this.recipeData);
    },
    displayPrint() {
      return !this.$route.query.autoprint;
    },
    recipeWarnings() {
      if (!this.recipeData || !this.isLoggedIn) return [];
      return this.getWarnings(this.recipeData.id);
    },
  },
  methods: {
    ...mapActions({
      computeRecipeWarnings: "recipeFilter/computeRecipeWarnings",
    }),
    async reset({ recipeId, recipe }) {
      if (!recipeId && !recipe) {
        return;
      }
      this.rating = {};
      if (recipe) {
        this.recipeData = recipe;
        this.onRecipeLoaded();
      } else {
        this.recipeData = await this.$store.dispatch("recipe/getRecipe", {
          recipeId,
          ratio: this.ratio,
        });
        this.onRecipeLoaded();
      }
    },
    printRecipe() {
      window.print();
    },
    /*
     * Switch a recipe in/out of cookbook -- if possible
     */
    async toggleFavorite() {
      if (this.isPersonal || this.toggleFavoriteInProgress) {
        return; // Personal recipe, no interaction
      }
      this.toggleFavoriteInProgress = true;
      if (!this.inCookbook) {
        this.inCookbook = true;
        await this.$store.dispatch("cookbook/addRecipe", this.recipeData.id);
        this.toggleFavoriteInProgress = false;
      } else {
        this.inCookbook = false;
        await this.$store.dispatch("cookbook/rmRecipe", this.recipeData.id);
        this.toggleFavoriteInProgress = false;
      }
    },
    updateFavoriteInfos() {
      if (this.isLoggedIn) {
        this.isPersonal = this.$store.getters["cookbook/recipeIsPersonal"](this.recipeData.id);
        this.inCookbook = this.$store.getters["cookbook/recipeInCookbook"](this.recipeData.id);
      }
    },
    onRecipeLoaded() {
      this.recipeData = { ...this.recipeData };
      this.updateFavoriteInfos();
      if (this.mayRate) {
        if (this.isLoggedIn) {
          API.recipe.userRating(this.recipeData.id).then((data) => {
            this.rating.existing = data;
          });
        }
        this.rating.value = null;
        this.rating.mouseover = null;
      }
      if (this.showRatings) {
        this.ratingsPage = { offset: 0, nbPerPage: 10 };
        this.refreshRatings();
      }
      if (this.isLoggedIn) {
        this.computeRecipeWarnings({ recipeId: this.recipeData.id });
      }
      this.fullUrl = "https://www.cookandbe.com" + recipePath(this.recipeData);
      if (this.$route.query.autoprint) {
        setTimeout(() => {
          // Let Vue display its items in the HTML first
          this.printRecipe();
        }, 300);
      }
    },
    async refreshRatings() {
      if (!this.recipeData) {
        return;
      }
      const data = await this.$store.dispatch("recipe/getRatings", {
        recipeId: this.recipeData.id,
        offset: this.ratingsPage.offset,
        limit: this.ratingsPage.nbPerPage,
      });
      this.recipeRatings = data; // Patch to avoid clipping
    },
    async onUpload(imgdata) {
      this.uploadInProgress = true;
      await API.recipeImgUpload(this.recipeData.id, { image: imgdata });
      this.uploadInProgress = false;
      this.reset({ recipe: this.recipe, recipeId: this.recipeId });
    },
    extractHostname(url) {
      return opParseUrl(url).hostname;
    },
    /*
     * The user selected a rating
     */
    setRating(value) {
      this.rating.value = value;
    },
    /*
     * Send the user ratings to the server
     */
    rateRecipe() {
      API.recipe.rate(this.recipeData.id, {
        rating: this.rating.value,
        comment: this.rating.comment,
      });
      this.rating.sentToServer = true;
    },
    /*
     * Switching to another page of ratings/comments
     */
    onChangeRatingsPage(page) {
      this.ratingsPage.offset = page.offset;
      this.refreshRatings();
    },
  },
  components: {
    ConditionalH1,
    Favorite,
    RecipeImg,
    InfosTag,
    RecipeWarnings,
    Ingredients,
    Instructions,
    AddRating,
    Ratings,
    RecipePrint,
    UploadButton,
  },
};
</script>

<style lang="scss">
@import "./common";

.recipe-viewer-content {
  .recipe-viewer-dishtypes {
    color: $op-color-red;
    font-size: $op-font-lg;
    width: 100%;
  }

  h2 {
    @extend .recipe-viewer-content__h2;
  }

  .recipe-attribute {
    padding: 0 5px;
  }

  .recipe-transclusion {
    clear: both;
    width: 100%;
    text-align: center;

    &:after {
      @extend .clearfix;
    }
  }

  .op-table {
    margin-bottom: 10px;
  }
}
</style>
