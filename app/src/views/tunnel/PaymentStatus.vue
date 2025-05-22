<template>
  <div id="payment-status" class="op-page">
    <div class="op-page-content">
      <div v-if="status === 'accepted'">
        <h2><FontAwesomeIcon :icon="['fas', 'check']" /> Abonnement réussi</h2>
        <div class="col-12 op-vs">
          <p>Toute l'équipe de Cook&amp;Be vous remercie pour votre confiance !</p>
        </div>
      </div>

      <div v-if="status !== 'accepted'">
        <h2 v-if="status === 'refused'">
          <FontAwesomeIcon :icon="['fas', 'times']" />
          Paiement refusé
        </h2>
        <h2 v-if="status === 'cancelled'">
          <FontAwesomeIcon :icon="['fas', 'times']" />
          Paiement annulé
        </h2>
        <h2 v-if="status === 'error'">
          <FontAwesomeIcon :icon="['fas', 'times']" />
          Une erreur a eu lieue lors du paiement
        </h2>

        <div class="col-12 op-vs">
          <p>Aucun paiement n'a été enregistré.</p>
          <p>Votre compte a été basculé sur l'offre gratuite.</p>
        </div>
      </div>

      <span class="clearfix" />

      <div class="payment-infos">
        <table class="payment-infos-table">
          <tr>
            <td class="d-none d-sm-table-cell">
              <div class="op-diet-card">
                <div class="op-diet-img">
                  <img :src="dietImage(currentDiet)" />
                </div>
                <div class="op-diet-title">{{ currentDiet.title }}</div>
              </div>
            </td>

            <td>
              <table class="op-vs payment-details-table">
                <tr>
                  <td>Votre abonnement</td>
                  <td class="detail">{{ SUBSCRIPTION_NAMES[currentSubscriptionLevel] }}</td>
                </tr>
                <tr>
                  <td>Votre alimentation</td>
                  <td class="detail">{{ currentDiet.title }}</td>
                </tr>
                <tr>
                  <td>
                    <p v-if="status === 'accepted'">Pour modifier votre alimentation, rendez-vous dans le menu</p>
                    <p v-if="status === 'cancelled'">Pour souscrire à un abonnement, rendez-vous dans le menu</p>
                    <p v-if="status === 'error'">Pour réessayer, rendez-vous dans le menu</p>
                    <p v-if="status === 'refused'">Pour réessayer, rendez-vous dans le menu</p>
                  </td>
                  <td>
                    <ul class="nav navbar-nav">
                      <MenuElt to="MyAccount" icon="apple-alt" caption="Mon alimentation" :displayOn="true" />
                    </ul>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </div>

      <div class="col-12 op-vs text-center">
        <a class="btn btn-success" href="" @click.prevent="returnToWebsite"> Retour à Cook&amp;Be </a>
      </div>
    </div>
  </div>
</template>

<script>
import MenuElt from "@/components/interface/MenuElt.vue";
import { mapGetters } from "vuex";
import { SUBSCRIPTION_NAMES } from "@/common/static.js";

export default {
  name: "PaymentStatus",
  props: [],
  data: () => ({
    SUBSCRIPTION_NAMES,
  }),
  computed: {
    ...mapGetters({
      user: "user/get",
      currentDiet: "user/getObjectiveDetails",
    }),
    currentSubscriptionLevel() {
      return this.user.subscriptionLevel;
    },
    status() {
      return this.$route.params.status;
    },
  },
  methods: {
    returnToWebsite() {
      if (this.status === "accepted") {
        this.$store.dispatch("configStage/redirectAfterSubscriptionModification");
      } else {
        this.$router.push({ name: "MyAccount" });
      }
    },
    dietImage(diet) {
      return require(`@/assets/img/objectives/header/${diet.key}.jpg`);
    },
  },
  components: { MenuElt },
};
</script>

<style scoped lang="scss">
#payment-status {
  .payment-infos {
    background-color: $op-color-grey-light;
    width: 100%;
  }

  .payment-infos-table {
    margin: auto;
    border-collapse: separate;
    border-spacing: 30px;
  }

  .payment-details-table {
    border-collapse: separate;
    border-spacing: 0px;

    td {
      height: 30px;
      max-width: 200px;
    }

    .detail {
      padding-left: 20px;
      font-weight: bold;
    }
  }
}
</style>
