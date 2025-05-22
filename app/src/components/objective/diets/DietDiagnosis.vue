<template>
  <SlimDiagnosis
    v-if="dietWithoutPrefix == 'slim'"
    :questions="questions"
    :profile="profile"
    @update:questions="$emit('update:questions', $event)"
    @update:profile="$emit('update:profile', $event)"
    @update:isValid="$emit('update:isValid', $event)"
  />
  <DiabeteDiagnosis
    v-if="dietWithoutPrefix == 'diabete'"
    :questions="questions"
    :profile="profile"
    @update:questions="$emit('update:questions', $event)"
    @update:profile="$emit('update:profile', $event)"
    @update:isValid="$emit('update:isValid', $event)"
  />
  <HypertensionDiagnosis
    v-if="dietWithoutPrefix == 'hypertension'"
    :questions="questions"
    :profile="profile"
    @update:questions="$emit('update:questions', $event)"
    @update:profile="$emit('update:profile', $event)"
    @update:isValid="$emit('update:isValid', $event)"
  />
  <NormolipidicDiagnosis
    v-if="dietWithoutPrefix == 'normolipidic'"
    :questions="questions"
    :profile="profile"
    @update:questions="$emit('update:questions', $event)"
    @update:profile="$emit('update:profile', $event)"
    @update:isValid="$emit('update:isValid', $event)"
  />
  <CardiovascularDiagnosis
    v-if="dietWithoutPrefix == 'cardiovascular'"
    :questions="questions"
    :profile="profile"
    @update:questions="$emit('update:questions', $event)"
    @update:profile="$emit('update:profile', $event)"
    @update:isValid="$emit('update:isValid', $event)"
  />
</template>

<script>
import SlimDiagnosis from "@/components/objective/diets/slim/SlimDiagnosis.vue";
import DiabeteDiagnosis from "@/components/objective/diets/diabete/DiabeteDiagnosis.vue";
import HypertensionDiagnosis from "@/components/objective/diets/hypertension/HypertensionDiagnosis.vue";
import NormolipidicDiagnosis from "@/components/objective/diets/normolipidic/NormolipidicDiagnosis.vue";
import CardiovascularDiagnosis from "@/components/objective/diets/cardiovascular/CardiovascularDiagnosis.vue";

import { ENABLE_DIET_FORCE_SLIM_DIAGNOSIS } from '@/config.js';

export default {
  name: "DietDiagnosis",
  props: ["diet", "questions", "profile"],
  data: () => ({}),
  computed: {
    dietWithoutPrefix () {
      if (ENABLE_DIET_FORCE_SLIM_DIAGNOSIS) {
        return 'slim';
      }
      return this.diet;
    }
  },
  methods: {},
  components: {
    SlimDiagnosis,
    DiabeteDiagnosis,
    HypertensionDiagnosis,
    NormolipidicDiagnosis,
    CardiovascularDiagnosis,
  },
};
</script>

<style scoped lang="scss"></style>
