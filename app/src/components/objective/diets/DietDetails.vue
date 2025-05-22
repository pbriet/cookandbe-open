<template>
  <SlimDetails v-if="diet == 'slim'" />
  <BalancedDetails v-if="diet == 'balanced'" />
  <GlutenFreeDetails v-if="diet == 'gluten_free'" />
  <VegetarianDetails v-if="diet == 'vegetarian'" />
  <VeganDetails v-if="diet == 'vegan'" />
  <DiabeteDetails v-if="diet == 'diabete'" />
  <EasyDigestDetails v-if="diet == 'easy_digest'" />
  <HypertensionDetails v-if="diet == 'hypertension'" />
  <NormolipidicDetails v-if="diet == 'normolipidic'" />
  <CardiovascularDetails v-if="diet == 'cardiovascular'" />
</template>

<script>
import SlimDetails from "@/components/objective/diets/slim/SlimDetails.vue";
import BalancedDetails from "@/components/objective/diets/balanced/BalancedDetails.vue";
import GlutenFreeDetails from "@/components/objective/diets/gluten_free/GlutenFreeDetails.vue";
import VegetarianDetails from "@/components/objective/diets/vegetarian/VegetarianDetails.vue";
import VeganDetails from "@/components/objective/diets/vegan/VeganDetails.vue";
import DiabeteDetails from "@/components/objective/diets/diabete/DiabeteDetails.vue";
import EasyDigestDetails from "@/components/objective/diets/easy_digest/EasyDigestDetails.vue";
import HypertensionDetails from "@/components/objective/diets/hypertension/HypertensionDetails.vue";
import NormolipidicDetails from "@/components/objective/diets/normolipidic/NormolipidicDetails.vue";
import CardiovascularDetails from "@/components/objective/diets/cardiovascular/CardiovascularDetails.vue";

export default {
  name: "DietDetails",
  props: ["diet"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {
    SlimDetails,
    BalancedDetails,
    GlutenFreeDetails,
    VegetarianDetails,
    VeganDetails,
    DiabeteDetails,
    EasyDigestDetails,
    HypertensionDetails,
    NormolipidicDetails,
    CardiovascularDetails,
  },
};
</script>

<style scoped lang="scss"></style>
