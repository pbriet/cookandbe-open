<template>
  <div id="op-payment-choice-page" class="op-page-public">
    <div class="op-page-title container">
      <h1>Récapitulatif</h1>
    </div>

    <div class="op-page-content container">
      <PaymentChoiceComponent />
    </div>
  </div>
</template>

<script>
import PaymentChoiceComponent from "@/components/tunnel/PaymentChoice";

export default {
  name: "PaymentChoice",
  props: [],
  data: () => ({}),
  computed: {},
  methods: {},
  components: { PaymentChoiceComponent },
};
</script>

<style scoped lang="scss"></style>
