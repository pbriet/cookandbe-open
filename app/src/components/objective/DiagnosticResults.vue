<template>
  <div id="op-diagnose">
    <DietResults :diet="diet.selected.key" :diagnosticResults="diagnosticResults" />

    <div v-if="showPremiumSelection">
      <PremiumChoice />
    </div>
    <div v-if="!showPremiumSelection">
      <button class="btn btn-success fright" @click="finalizeDietSelectionNoPayment">Continuer</button>
    </div>
  </div>
</template>

<script>
import PremiumChoice from "@/components/tunnel/premium_choice/PremiumChoice.vue";
import DietResults from "@/components/objective/diets/DietResults.vue";

export default {
  name: "DiagnosticResults",
  props: ["diet", "showPremiumSelection", "finalizeDietSelectionNoPayment", "diagnosticResults"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: { PremiumChoice, DietResults },
};
</script>

<style scoped lang="scss"></style>
