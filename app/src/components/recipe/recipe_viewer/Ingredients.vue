<template>
  <div class="col-12 recipe-viewer-ingredients ps-0" :class="{ print: printMode }">
    <ConditionalH2 :when="!printMode">
      <span>
        Ingrédients
        <span v-if="eaterIds">
          pour
          <span v-for="(eaterId, index) in eaterIds" :key="eaterId">
            <span v-if="index != 0">, </span>
            {{ getEaterById(eaterId).profile.nickname }}
          </span>
        </span>
        <span v-if="!ratio && !eaterIds" itemprop="recipeYield">
          pour {{ nbPeople }}
          <span v-if="nbPeople == 1">personne</span>
          <span v-if="nbPeople > 1">personnes</span>
        </span>
      </span>
    </ConditionalH2>
    <ul class="mb-0">
      <li v-for="ingredient in sortedIngredients" :key="ingredient.id">
        <span class="recipe-viewer-ingredient-name" itemprop="ingredients">{{ ingredient.name }}</span>
        <span v-if="ingredient.conversions.best.value > 0">
          :
          <span
            class="recipe-viewer-ingredient-quantity"
            v-html="conversionClean(ingredient.conversions.best, ingredient.name)"
          >
          </span>
          <span v-if="ingredient.conversions.basic?.unit">
            (<span v-html="ingredient.conversions.basic.htmlValue"></span> {{ ingredient.conversions.basic.unit }})
          </span>
        </span>
        <span
          class="recipe-viewer-ingredient-state"
          v-if="ingredient.rawStateName !== 'frais' && ingredient.conversions.best.grams > 0"
        >
          ({{ ingredient.rawStateName }})
        </span>
      </li>
    </ul>
  </div>
</template>

<script>
import { sortBy } from "lodash";
import { mapGetters } from "vuex";
import { conversionClean } from "@/common/filters.js";
import ConditionalH2 from "@/components/interface/conditional_headers/ConditionalH2.vue";

export default {
  name: "Ingredients",
  props: ["printMode", "eaterIds", "ratio", "nbPeople", "ingredients"],
  data: () => ({}),
  computed: {
    ...mapGetters({
      getEaterById: "profile/getEaterById",
    }),
    sortedIngredients() {
      return sortBy(this.ingredients, (ingredient) => -ingredient.grams);
    },
  },
  methods: {
    conversionClean,
  },
  components: { ConditionalH2 },
};
</script>

<style scoped lang="scss">
.recipe-viewer-ingredients:not(.print) {
  clear: both;

  .recipe-viewer-ingredient-name {
    color: $op-color-green;
  }

  .recipe-viewer-ingredient-state {
    color: $op-color-text-soft;
  }
}
</style>
