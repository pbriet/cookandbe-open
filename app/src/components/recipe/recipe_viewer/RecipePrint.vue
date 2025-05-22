<template>
  <div class="op-recipe-viewer-print" v-if="recipeData">
    <ConditionalH1 :when="false">
      <span>{{ recipeData.name }}</span>
    </ConditionalH1>
    <ConditionalH3 :when="false">
      <span>{{ APP_BRAND_NAME }} - {{ getDishTypes }}</span>
    </ConditionalH3>
    <RatingStars :value="recipeData.avgRating" :withValues="true" />

    <div class="row">
      <!-- Ingredients -->
      <div class="col-8" v-if="showDetails">
        <Ingredients
          :eaterIds="eaterIds"
          :ratio="ratio"
          :nbPeople="recipeData.nbPeople"
          :ingredients="recipeData.ingredients"
          :printMode="true"
        />
      </div>
      <!-- Infos -->
      <div class="col-4" v-if="showDetails && !recipeData.internal">
        <Infos :recipeData="recipeData" :extractHostname="extractHostname" :canEditRecipe="canEditRecipe" />
      </div>
    </div>

    <div v-if="showDetails" class="row ps-3">
      <Instructions :printMode="true" :instructions="recipeData.instructions" />
    </div>
  </div>
</template>

<script>
import { APP_BRAND_NAME } from "@/config.js";
import RatingStars from "@/components/interface/RatingStars.vue";
import Ingredients from "@/components/recipe/recipe_viewer/Ingredients.vue";
import Instructions from "@/components/recipe/recipe_viewer/Instructions.vue";
import Infos from "@/components/recipe/recipe_viewer/Infos.vue";
import ConditionalH1 from "@/components/interface/conditional_headers/ConditionalH1.vue";
import ConditionalH3 from "@/components/interface/conditional_headers/ConditionalH3.vue";

export default {
  name: "RecipePrint",
  props: ["recipeData", "showDetails", "ratio", "eaterIds", "getDishTypes", "extractHostname", "canEditRecipe"],
  data: () => ({
    APP_BRAND_NAME,
  }),
  computed: {},
  methods: {},
  components: { RatingStars, ConditionalH1, ConditionalH3, Infos, Ingredients, Instructions },
};
</script>

<style lang="scss">
@import "./common";

.op-recipe-viewer-print {
  @page {
    size: portrait;
  }

  .conditional-h1 {
    @extend .h1;
  }
  .conditional-h2 {
    @extend .h2;
    @extend .recipe-viewer-content__h2;
  }
  .conditional-h3 {
    @extend .h3;
  }

  .conditional-h1,
  .conditional-h2,
  .conditional-h3 {
    display: block;
    margin-top: 0;
    margin-bottom: 0;
    line-height: 1.43;
  }

  .recipe-viewer-infos {
    border: 1px solid black !important;
    & > span {
      width: 100% !important;
    }
  }
  .recipe-infos-times {
    & > span {
      width: 100% !important;
    }
  }
}
</style>
