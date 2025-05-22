<template>
  <SlimSummary v-if="dietWithoutPrefix == 'slim'" />
  <BalancedSummary v-if="dietWithoutPrefix == 'balanced'" />
  <GlutenFreeSummary v-if="dietWithoutPrefix == 'gluten_free'" />
  <VegetarianSummary v-if="dietWithoutPrefix == 'vegetarian'" />
  <VeganSummary v-if="dietWithoutPrefix == 'vegan'" />
  <DiabeteSummary v-if="dietWithoutPrefix == 'diabete'" />
  <EasyDigestSummary v-if="dietWithoutPrefix == 'easy_digest'" />
  <HypertensionSummary v-if="dietWithoutPrefix == 'hypertension'" />
  <NormolipidicSummary v-if="dietWithoutPrefix == 'normolipidic'" />
  <CardiovascularSummary v-if="dietWithoutPrefix == 'cardiovascular'" />
</template>

<script>
import SlimSummary from "@/components/objective/diets/slim/SlimSummary.vue";
import BalancedSummary from "@/components/objective/diets/balanced/BalancedSummary.vue";
import GlutenFreeSummary from "@/components/objective/diets/gluten_free/GlutenFreeSummary.vue";
import VegetarianSummary from "@/components/objective/diets/vegetarian/VegetarianSummary.vue";
import VeganSummary from "@/components/objective/diets/vegan/VeganSummary.vue";
import DiabeteSummary from "@/components/objective/diets/diabete/DiabeteSummary.vue";
import EasyDigestSummary from "@/components/objective/diets/easy_digest/EasyDigestSummary.vue";
import HypertensionSummary from "@/components/objective/diets/hypertension/HypertensionSummary.vue";
import NormolipidicSummary from "@/components/objective/diets/normolipidic/NormolipidicSummary.vue";
import CardiovascularSummary from "@/components/objective/diets/cardiovascular/CardiovascularSummary.vue";

export default {
  name: "DietSummary",
  props: ["diet"],
  data: () => ({}),
  computed: {
    dietWithoutPrefix () {
      return this.diet;
    }
  },
  methods: {},
  components: {
    SlimSummary,
    BalancedSummary,
    GlutenFreeSummary,
    VegetarianSummary,
    VeganSummary,
    DiabeteSummary,
    EasyDigestSummary,
    HypertensionSummary,
    NormolipidicSummary,
    CardiovascularSummary,
  },
};
</script>

<style scoped lang="scss"></style>
