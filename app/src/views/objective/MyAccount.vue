<template>
  <div id="op-my-objective" class="op-page">
    <div class="op-page-title">
      <h1>Mon alimentation</h1>
    </div>

    <div class="op-page-content">
      <div class="row">
        <div class="col-12 col-md-6" v-if="ENABLE_NUTRIENT_PACKS">
          <h2>Nutriments contrôlés</h2>

          <div id="controlled-nutrients-header">
            <div class="alert alert-warning" v-if="getNbEnabledPacks >= 2">
              Il n'est pas possible d'activer plus de 2 packs simultanément.<br />
              Déselectionnez-en un pour pouvoir en activer un autre.
            </div>
            <div class="info-block" v-if="getNbEnabledPacks == 1">
              <FontAwesomeIcon :icon="['fas', 'info-circle']" /> Les suggestions {{ APP_BRAND_NAME }} sont garanties
              équilibrées sur les nutriments ci-dessous.<br />
              Vous pouvez choisir un pack nutritionnel qui viendra s'ajouter à l'équilibre de base.
            </div>
          </div>

          <div v-for="pack in nutrientPacks" class="nutrient-pack" :key="pack.id">
            <ToggleSwitch
              v-model="pack.enabled"
              :readonly="!pack.canBeUnchecked || (getNbEnabledPacks >= 2 && !pack.enabled)"
              :onChange="() => toggleNutrientPack(pack)"
            />

            <h4>{{ pack.title }}</h4>

            <p>{{ pack.description }}</p>

            <ul>
              <li v-for="group in pack.indicatorsPerGroup" :key="group.title">
                {{ group.title }} :
                <span v-for="(nut, index) in group.nutrients" :key="nut.key">
                  <span v-if="index != 0">, </span>
                  {{ upperFirst(INDICATOR_TITLE[nut.key]) }}
                </span>
              </li>
            </ul>

            <i class="text-danger" v-if="pack.enabled && pack.warning">
              {{ pack.warning }}
            </i>
          </div>
        </div>

        <!-- col-12 col-md-6 -->
        <div class="col-12 col-md-6 text-center" :class="{'col-md-6': !ENABLE_NUTRIENT_PACKS}">
          <h2><span v-if="ENABLE_PUBLIC_PAYMENT">Abonnement / </span>Alimentation</h2>

          <div class="op-font-xl op-diet-card">
            <div class="deactivated-diet-cross" v-if="ENABLE_PUBLIC_PAYMENT && currentDiet.key !== wantedDiet.key">
              <img src="~@/assets/img/forbidden.png" />
            </div>
            <div class="op-diet-img">
              <img :src="wantedDietImage" :class="{ 'deactivated-diet-img': currentDiet.key !== wantedDiet.key }" />
            </div>
            <div class="op-diet-title">{{ wantedDiet.title }}</div>
          </div>

          <div class="op-vs-20">
            <router-link
              class="btn btn-secondary change-diet-btn"
              :to="{ name: 'DietChoice', query: { from_account: 1 } }"
            >
              Changer d'alimentation
            </router-link>
          </div>

          <div
            v-if="
              wantedDiet.minSubscriptionLevel > 0 &&
              (freeTrial || currentSubscription.level == 0) &&
              wantedDietDiscount > 0 &&
              ENABLE_PUBLIC_PAYMENT
            "
            class="op-font-red op-font-xxl op-vs"
          >
            PROMOTION EXCEPTIONNELLE : -{{ wantedDietDiscount }}%
            <div class="op-font-md">
              En ce moment, -{{ wantedDietDiscount }}% sur l'alimentation {{ wantedDiet.title }}.<br />
              Offre limitée dans le temps. Profitez-en dès maintenant !
            </div>
            <div class="op-vs">
              <router-link
                class="btn btn-success"
                :to="{ name: 'PaymentChoice', params: { level: wantedDiet.minSubscriptionLevel } }"
              >
                Acheter maintenant
              </router-link>
            </div>
          </div>

          <div
            v-if="
              currentSubscription.level == 0 &&
              wantedDiet.minSubscriptionLevel == 0 &&
              premiumDiscount > 0 &&
              ENABLE_PUBLIC_PAYMENT
            "
            class="op-font-red op-font-xxl op-vs"
          >
            PROMOTION EXCEPTIONNELLE : -{{ premiumDiscount }}%
            <div class="op-font-md">
              En ce moment, -{{ premiumDiscount }}% sur l'abonnement Premium.<br />
              Offre limitée dans le temps. Profitez-en dès maintenant !
            </div>
            <div class="op-vs">
              <router-link class="btn btn-success" :to="{ name: 'PaymentChoice', params: { level: 1 } }">
                Acheter maintenant
              </router-link>
            </div>
          </div>

          <div
            v-if="
              currentSubscription.level == 0 &&
              wantedDiet.minSubscriptionLevel == 0 &&
              premiumDiscount == 0 &&
              ENABLE_PUBLIC_PAYMENT
            "
            class="op-font-xxl op-vs"
          >
            Choisissez un abonnement Premium
            <div class="op-font-md">
              Accédez à de nouvelles alimentations, avec un diététicien prêt à répondre à vos questions.<br />
              A partir de 10€/mois seulement !
            </div>
            <div class="op-vs">
              <router-link class="btn btn-success" :to="{ name: 'PaymentChoice', params: { level: 1 } }">
                Acheter maintenant
              </router-link>
            </div>
          </div>

          <PremiumTrophy
            :level="currentSubscription.level"
            v-if="currentSubscription.level != 0 && ENABLE_PUBLIC_PAYMENT"
          />
          <div class="op-diet-details" v-if="ENABLE_PUBLIC_PAYMENT">
            <div v-if="currentDiet.key !== wantedDiet.key" class="op-diet-not-activated">
              <div>
                <div class="op-alert-activated">
                  <FontAwesomeIcon :icon="['fas', 'exclamation-circle']" />
                  Pour activer cette alimentation, vous devez prendre un abonnement
                  {{ SUBSCRIPTION_NAMES[wantedDiet.minSubscriptionLevel] }}
                </div>
                <br />
                <router-link
                  class="btn btn-warning"
                  :to="{ name: 'PaymentChoice', params: { level: wantedDiet.minSubscriptionLevel } }"
                >
                  Passer en {{ SUBSCRIPTION_NAMES[wantedDiet.minSubscriptionLevel] }}
                </router-link>
              </div>
              <br />
              Tant que vous n'aurez pas pris d'abonnement, vous bénéficiez gratuitement d'une
              <b>alimentation équilibrée</b>, avec contrôle des apports sur 30 nutriments.<br />
            </div>
            <!-- op-diet-not-activated -->

            <div v-if="currentSubscription.level > 0" class="op-vs-20 op-font-lg">
              <span class="me-1">
                <FontAwesomeIcon :icon="['fas', 'check']" />
              </span>
              <span v-if="!freeTrial">Vous êtes abonné(e)</span>
              <span v-if="freeTrial">Vous bénéficiez d'une période d'essai gratuite</span>
              jusqu'au
              <b>{{
                currentSubscription.endDate &&
                DateTime.fromFormat(currentSubscription.endDate, "yyyy-MM-dd").setLocale("fr").toFormat("dd MMMM yyyy")
              }}</b
              >.
              <br />
              <router-link
                class="btn btn-secondary"
                v-if="wantedDiet.minSubscriptionLevel > 0 && wantedDietDiscount == 0 && freeTrial"
                :to="{ name: 'PaymentChoice', params: { level: wantedDiet.minSubscriptionLevel } }"
              >
                Acheter maintenant
              </router-link>
            </div>
          </div>
          <!-- op-diet-details col-12 col-md-6 -->
        </div>
        <!-- col-12  /  col-md-6 -->
      </div>
      <!-- row -->
    </div>
    <!-- op-page-content -->
  </div>
  <!-- op-page -->
</template>

<script>
import { upperFirst } from "lodash";
import { mapGetters } from "vuex";
import { ENABLE_PUBLIC_PAYMENT, ENABLE_NUTRIENT_PACKS, APP_BRAND_NAME } from "@/config.js";
import { SUBSCRIPTION_NAMES } from "@/common/static.js";
import { INDICATOR_TITLE } from "@/_data.js";
import { DateTime } from "luxon";
import ToggleSwitch from "@/components/interface/ToggleSwitch.vue";
import PremiumTrophy from "@/components/tunnel/premium_choice/PremiumTrophy.vue";

export default {
  name: "MyAccount",
  props: [],
  data: () => ({
    APP_BRAND_NAME,
    SUBSCRIPTION_NAMES,
    ENABLE_PUBLIC_PAYMENT,
    ENABLE_NUTRIENT_PACKS,
    INDICATOR_TITLE,
    DateTime,
  }),
  computed: {
    ...mapGetters({
      user: "user/get",
      levelDiscount: "diet/levelDiscount",
      nutrientPacks: "diet/getNutrientPacks",
      getNbEnabledPacks: "diet/getNbEnabledPacks",
    }),
    currentDiet() {
      return this.user.objective;
    },
    wantedDiet() {
      return this.user.wantedObjective;
    },
    premiumDiscount() {
      return ENABLE_PUBLIC_PAYMENT ? this.levelDiscount(1) : 0;
    },
    freeTrial() {
      return ENABLE_PUBLIC_PAYMENT ? this.user.freeTrial.enabled : false;
    },
    wantedDietDiscount() {
      return ENABLE_PUBLIC_PAYMENT ? this.levelDiscount(this.wantedDiet.minSubscriptionLevel) : 0;
    },
    currentSubscription() {
      return {
        level: this.user.subscriptionLevel,
        canResiliate: this.user.canResiliate,
        endDate: this.user.subscriptionEndDate,
      };
    },
    wantedDietImage() {
      return require(`@/assets/img/objectives/header/${this.wantedDiet.key}.jpg`);
    },
  },
  methods: {
    toggleNutrientPack(pack) {
      this.$store.dispatch("diet/enablePack", { packKey: pack.key, enabled: pack.enabled });
    },
    upperFirst,
  },
  components: { PremiumTrophy, ToggleSwitch },
};
</script>

<style scoped lang="scss">
#op-my-objective {
  .op-diet-not-activated {
    .op-alert-activated {
      font-weight: bold;
      font-size: $op-font-xl;
      svg {
        padding-bottom: 2px;
      }
    }
    .btn-warning {
      background-color: $op-color-subscription-premium;
      color: white;
      border-color: lighten($op-color-subscription-premium, 10%) !important;
      &:hover {
        background-color: lighten($op-color-subscription-premium, 10%);
      }
    }
  }

  .op-diet-card {
    .op-diet-title {
      @media (max-width: $bootstrap-xs-max) {
        position: absolute;
      }
    }

    .deactivated-diet-cross {
      position: absolute;
      width: 100%;
      padding-top: 10px;

      img {
        height: 100%;
      }

      @media (min-width: $bootstrap-sm-min) {
        height: 70%;
      }
      @media (max-width: $bootstrap-xs-max) {
        height: 50%;
      }
    }
    .deactivated-diet-img {
      opacity: 0.4;
    }

    margin: auto;
  }

  h2 {
    padding-bottom: 20px;
  }

  .nutrient-pack {
    margin-bottom: 50px;
    h4 {
      padding-left: 10px;
      display: inline;
    }
    p {
      margin-top: 10px;
      font-weight: bold;
    }
  }

  #controlled-nutrients-header {
    height: 120px;
  }

  .info-block {
    padding: 15px;
    width: 100%;
    background-color: $op-color-grey-light;
  }
}
</style>
