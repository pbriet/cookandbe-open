<template>
  <PremiumTrophy :level="selectedLevel" />

  <div class="col-12 col-sm-7 col-md-5 op-font-xl op-diet-card mt-3">
    <div class="op-diet-img">
      <img :src="dietImage(wantedDiet)" />
    </div>
    <div class="op-diet-title">{{ wantedDiet.title }}</div>
  </div>

  <div class="clearfix"></div>

  <div class="row">
    <div class="col-12 op-subscription-selector" v-if="tariff">
      <h2>Je choisis la durée de mon abonnement :</h2>

      <table class="op-table">
        <tr
          v-for="tariffChoice in tariffChoices"
          :key="tariffChoice.nbMonths"
          @click="onSelectOffer(tariffChoice.nbMonths)"
        >
          <td style="padding: 2px 0px 2px 5px; width: 20px">
            <input
              type="radio"
              v-model="paymentOptions.nbMonths"
              :value="tariffChoice.nbMonths"
              :checked="paymentOptions.nbMonths == tariffChoice.nbMonths"
            />
          </td>
          <td style="width: 110px">{{ tariffChoice.nbMonths }} mois</td>
          <td class="d-none d-sm-table-cell" style="width: 80px" v-if="tariffChoice.discount">
            <span class="op-payment-discount">-{{ tariffChoice.discount }} %</span>
          </td>
          <td>
            <b>{{ tariffChoice.afterDiscount }}€ / mois</b><br class="d-sm-none" /><span class="d-none d-sm-inline"
              >, </span
            >soit {{ tariffChoice.afterDiscount * tariffChoice.nbMonths }}€
            <span class="d-sm-none op-payment-discount" v-if="tariffChoice.discount"
              ><br />(-{{ tariffChoice.discount }} %)</span
            >
          </td>
          <td class="op-payment-caption d-none d-sm-table-cell">
            {{ tariffChoice.caption }}
          </td>
        </tr>
      </table>
    </div>
    <!-- col-12 -->
  </div>
  <!-- row -->

  <div class="row">
    <div class="col-12 op-vs-10 row" v-if="!redirectionToPaybox">
      <div class="col-6 col-sm-4 col-md-3">
        <div
          class="btn btn-success col-12"
          @click="buy"
          :disabled="!paymentOptions.nbMonths"
          :class="{ disabled: !paymentOptions.nbMonths }"
        >
          Commander
        </div>
      </div>
      <div class="col-6 col-sm-4 col-md-3">
        <a class="btn btn-secondary col-12" href="" @click.prevent="goBack">Retour</a>
      </div>
    </div>
  </div>
  <!-- row -->
  <PleaseWait v-if="redirectionToPaybox" />
</template>

<script>
import { mapGetters } from "vuex";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import PremiumTrophy from "@/components/tunnel/premium_choice/PremiumTrophy.vue";

export default {
  name: "PaymentChoice",
  props: [],
  data: () => ({
    paymentOptions: {}, // {nbMonths: Number of months}
    redirectionToPaybox: false,
  }),
  computed: {
    ...mapGetters({
      user: "user/get",
      levelTariff: "diet/levelTariff",
    }),
    // Which subscription (from the URL)
    selectedLevel() {
      if (this.$route.params.level) {
        return this.$route.params.level;
      } else {
        return this.wantedDiet.minSubscriptionLevel;
      }
    },
    tariff() {
      return this.levelTariff(this.selectedLevel);
    },
    tariffChoices() {
      return [
        { nbMonths: 1, caption: "", afterDiscount: this.monthlyTariff(1), discount: this.discount(1) },
        {
          nbMonths: 3,
          caption: "le plus populaire !",
          afterDiscount: this.monthlyTariff(3),
          discount: this.discount(3),
        },
        { nbMonths: 12, caption: "", afterDiscount: this.monthlyTariff(12), discount: this.discount(12) },
      ];
    },
    wantedDiet() {
      return this.user.wantedObjective;
    },
  },
  methods: {
    monthlyTariff(nbMonths) {
      return this.tariff[nbMonths].afterDiscount;
    },
    discount(nbMonths) {
      return this.tariff[nbMonths].discount;
    },
    onSelectOffer(nbMonths) {
      this.paymentOptions.nbMonths = nbMonths;
    },
    buy() {
      this.redirectionToPaybox = true;
      const nbMonths = this.paymentOptions.nbMonths;
      const totalAmount = nbMonths * this.monthlyTariff(nbMonths);
      this.$store.dispatch("analytics/sendEvent", {
        category: "flow",
        action: "click",
        label: "buy_button",
        value: totalAmount,
      });
      // Redirection to payment
      window.location.href =
        "/payment/pay/?subscription_level=" +
        this.selectedLevel +
        "&nb_months=" +
        this.paymentOptions.nbMonths +
        "&user_id=" +
        this.user.id.toString();
    },
    goBack() {
      this.$router.go(-1);
    },
    dietImage(diet) {
      return require(`@/assets/img/objectives/header/${diet.key}.jpg`);
    },
  },
  components: { PleaseWait, PremiumTrophy },
};
</script>

<style scoped lang="scss">
.op-subscription-selector {
  margin-top: 20px;
  table {
    margin-top: 8px;
    margin-bottom: 10px;
    font-size: $op-font-lg;
    max-width: 700px;
    line-height: 25px;
    td {
      padding: 10px;
    }
    tr:hover {
      background-color: lighten($op-color-lime, 10%);
      cursor: pointer;
    }
  }
  font-size: $op-font-md;
  .op-payment-caption {
    color: $op-color-lime;
    font-weight: bold;
    font-size: $op-font-md;
  }

  .op-payment-discount {
    color: $op-color-alert-danger;
    font-weight: bold;
    font-size: $op-font-md;
  }
}
</style>
