<template>
  <div class="op-page">
    <div class="op-page-title">
      <h1>Votre abonnement a expiré</h1>
    </div>
    <div class="op-page-content">
      <p class="op-vs-10 op-font-lg">
        Pour continuer à bénéficier de vos services, merci de souscrire à un nouvel abonnement.
      </p>

      <div>
        <PremiumChoice />
      </div>
    </div>
  </div>
</template>

<script>
import PremiumChoice from "@/components/tunnel/premium_choice/PremiumChoice.vue";

export default {
  name: "Expired",
  props: [],
  data: () => ({}),
  computed: {},
  methods: {},
  components: { PremiumChoice },
};
</script>

<style scoped lang="scss"></style>
