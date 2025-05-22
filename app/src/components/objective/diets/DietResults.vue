<template>
  <SlimResults v-if="diet == 'slim'" :diagnosticResults="diagnosticResults" />
  <DiabeteResults v-if="diet == 'diabete'" :diagnosticResults="diagnosticResults" />
  <HypertensionResults v-if="diet == 'hypertension'" :diagnosticResults="diagnosticResults" />
  <NormolipidicResults v-if="diet == 'normolipidic'" :diagnosticResults="diagnosticResults" />
  <CardiovascularResults v-if="diet == 'cardiovascular'" :diagnosticResults="diagnosticResults" />
</template>

<script>
import SlimResults from "@/components/objective/diets/slim/SlimResults.vue";
import DiabeteResults from "@/components/objective/diets/diabete/DiabeteResults.vue";
import HypertensionResults from "@/components/objective/diets/hypertension/HypertensionResults.vue";
import NormolipidicResults from "@/components/objective/diets/normolipidic/NormolipidicResults.vue";
import CardiovascularResults from "@/components/objective/diets/cardiovascular/CardiovascularResults.vue";

export default {
  name: "DietResults",
  props: ["diet", "diagnosticResults"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: { SlimResults, DiabeteResults, HypertensionResults, NormolipidicResults, CardiovascularResults },
};
</script>

<style scoped lang="scss"></style>
