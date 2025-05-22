<template>
  <div id="op-premium-selection" class="op-page-public">
    <div class="op-page-title container">
      <h1>Choisissez votre abonnement</h1>
    </div>

    <div class="op-page-content container">
      <PremiumChoiceComponent />
    </div>
  </div>
</template>

<script>
import PremiumChoiceComponent from "@/components/tunnel/premium_choice/PremiumChoice.vue";
import { mapGetters } from "vuex";

export default {
  name: "PremiumChoice",
  props: [],
  data: () => ({}),
  mounted() {
    if (this.user.freeTrial.enabled) {
      // Free trial in progress. It is not possible to modify diet / subscription
      this.$router.push({ name: "MyAccount" });
    }
  },
  computed: {
    ...mapGetters({
      user: "user/get",
    }),
  },
  methods: {},
  components: { PremiumChoiceComponent },
};
</script>

<style lang="scss"></style>
