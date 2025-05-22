<template>
  <button class="btn btn-secondary" @click="selectSubscription(comparedSubscription)">
    <span v-if="!ENABLE_PUBLIC_PAYMENT"> Sélectionner </span>
    <span v-if="ENABLE_PUBLIC_PAYMENT">
      <span v-if="comparedSubscription === 0"> C'EST PARTI ! </span>
      <span v-if="comparedSubscription > 0">
        <span v-if="freeTrialAvailable">
          ESSAI GRATUIT<br />
          Pendant {{ wantedDiet.freeTrialDays }} jours
        </span>
        <span v-if="!freeTrialAvailable">
          A partir de
          <span
            v-if="levelLowestTariffsWithoutDiscount[comparedSubscription] != levelLowestTariffs[comparedSubscription]"
            class="previous-cost"
          >
            {{ levelLowestTariffsWithoutDiscount[comparedSubscription] }} €</span
          >
          {{ levelLowestTariffs[comparedSubscription] }}€/mois
        </span>
      </span>
    </span>
  </button>
</template>

<script>
import { mapGetters } from "vuex";
import { ENABLE_PUBLIC_PAYMENT } from "@/config.js";

export default {
  name: "SubscriptionBtn",
  props: ["comparedSubscription", "selectSubscription", "freeTrialAvailable"],
  data: () => ({
    ENABLE_PUBLIC_PAYMENT,
  }),
  computed: {
    ...mapGetters({
      user: "user/get",
    }),
    levelLowestTariffs() {
      return this.$store.getters["diet/levelLowestTariffs"]();
    },
    levelLowestTariffsWithoutDiscount() {
      return this.$store.getters["diet/levelLowestTariffs"](true);
    },
    wantedDiet() {
      return this.user.wantedObjective;
    },
  },
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
