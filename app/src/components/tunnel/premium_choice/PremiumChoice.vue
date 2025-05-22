<template>
  <PleaseWait v-if="activationInProgress" />

  <div v-if="!activationInProgress" class="premium-choices">
    <div>
      <div class="text-center container-fluid">
        <SubscriptionBtn
          v-if="!ENABLE_PUBLIC_PAYMENT"
          :freeTrialAvailable="freeTrialAvailable"
          :selectSubscription="selectSubscription"
        />
        <div
          id="subscription-table"
          v-if="ENABLE_PUBLIC_PAYMENT"
          :class="comparedSubscriptions.length === 1 ? 'mono-choice' : 'multi-choice'"
        >
          <div
            v-for="comparedSubscription in comparedSubscriptions"
            :key="comparedSubscription"
            class="subscription-column"
            :class="comparedSubscription === 0 ? 'default-subscription' : 'premium-subscription'"
          >
            <div class="subscription-tab">
              <h3 class="op-vs-5">
                {{ SUBSCRIPTION_NAMES[comparedSubscription] }}
              </h3>

              <div class="column-content">
                <Level :level="comparedSubscription" />
                <div class="premium-diet-activated">
                  <div
                    v-if="comparedSubscription === 0"
                    class="row"
                    :class="{ 'free-option-without-diet': wantedDiet.minSubscriptionLevel > 0 }"
                  >
                    <div class="col-12 col-md-4">
                      <img src="@/assets/img/objectives/balanced.jpg" />
                    </div>
                    <div class="col-12 col-md-8 premium-details">
                      <p v-if="wantedDiet.minSubscriptionLevel > 0" class="unactivated-diet">
                        {{ wantedDiet.title }}
                      </p>
                      <b>Equilibre, sans gluten ou végétarien</b>
                      <p>100% gratuit sur ces 3 alimentations uniquement</p>
                    </div>
                  </div>
                  <div v-if="comparedSubscription > 0 && wantedDiet.minSubscriptionLevel > 0" class="row">
                    <div class="col-12 col-md-4">
                      <img :src="wantedDietImage(wantedDiet)" />
                    </div>
                    <div class="col-12 col-md-8 premium-details">
                      <b>{{ wantedDiet.title }}</b>
                      <p>A la pointe de la nutrition.</p>
                      <br />
                    </div>
                  </div>
                  <div v-if="comparedSubscription > 0 && wantedDiet.minSubscriptionLevel == 0" class="row">
                    <div class="col-12 col-md-4">
                      <img src="@/assets/img/objectives/header/diabete.jpg" />
                    </div>
                    <div class="col-12 col-md-8 premium-details">
                      <b>Mode minceur</b>
                      <p>Retrouvez la ligne en douceur</p>
                      <br />
                    </div>
                  </div>
                  <!-- row -->
                </div>
                <!-- column-content -->
              </div>
              <!-- premium-diet-activated -->
            </div>
            <!-- subscription-tab -->

            <div class="d-md-none">
              <SubscriptionBtn
                :freeTrialAvailable="freeTrialAvailable"
                :selectSubscription="selectSubscription"
                :comparedSubscription="comparedSubscription"
              />
            </div>
          </div>
          <!-- subscription-column -->

          <div class="d-none d-md-table-row">
            <div
              v-for="comparedSubscription in comparedSubscriptions"
              :key="comparedSubscription"
              style="display: table-cell"
              :class="comparedSubscription === 0 ? 'default-subscription' : 'premium-subscription'"
            >
              <SubscriptionBtn
                :freeTrialAvailable="freeTrialAvailable"
                :selectSubscription="selectSubscription"
                :comparedSubscription="comparedSubscription"
              />
            </div>
          </div>
        </div>
        <!-- subscription-table -->
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { ENABLE_PUBLIC_PAYMENT } from "@/config.js";
import { SUBSCRIPTION_NAMES } from "@/common/static.js";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import SubscriptionBtn from "@/components/tunnel/premium_choice/SubscriptionBtn.vue";
import Level from "@/components/tunnel/premium_choice/Level.vue";
import API from "@/api.js";

export default {
  name: "PremiumChoice",
  data: () => ({
    ENABLE_PUBLIC_PAYMENT,
    SUBSCRIPTION_NAMES,
    activationInProgress: false,
  }),
  computed: {
    ...mapGetters({
      userId: "user/id",
      user: "user/get",
      recentlyJoined: "user/recentlyJoined",
      levelDiscount: "diet/levelDiscount",
    }),
    forceLevel() {
      return this.$route.query.level || 0;
    },
    wantedDiet() {
      return this.user.wantedObjective;
    },
    freeTrialAvailable() {
      if (ENABLE_PUBLIC_PAYMENT) {
        // Do we activate a free trial ? YES if :
        // - User has never consumed a free trial
        // - User is a new one OR there is no discount currently applied on the diet level
        return (
          !this.user.freeTrial.consumed &&
          (this.recentlyJoined || this.levelDiscount(this.wantedDiet.minSubscriptionLevel) === 0)
        );
      } else {
        return false;
      }
    },
    comparedSubscriptions() {
      const requiredLevel = Math.max(this.wantedDiet.minSubscriptionLevel, this.forceLevel);
      if (requiredLevel === 0) {
        // Free or "Freedom" diets
        // Compare the two first levels of subscription only
        return [1, 0];
      } else {
        // Premium diet
        // Compare free and premium
        if (this.freeTrialAvailable) {
          // Trial is available
          // Don't display the free version yet
          return [requiredLevel];
        } else {
          return [requiredLevel, 0];
        }
      }
    },
  },
  methods: {
    async selectSubscription(level) {
      if (level === 0 || !ENABLE_PUBLIC_PAYMENT) {
        // Free offer. Go to configuration
        this.$store.dispatch("configStage/redirectAfterSubscriptionModification");
        return;
      }
      if (this.freeTrialAvailable) {
        this.activationInProgress = true;
        // Free trial : activate it and go to configuration
        await API.activateFreeTrial(this.userId);
        // Refresh user : now, trial is consumed
        await this.$store.dispatch("user/load");
        this.$store.dispatch("configStage/redirectAfterSubscriptionModification");
        return;
      }
      // Requires payment
      this.$router.push({ name: "PaymentChoice", params: { level } });
    },
    wantedDietImage(wantedDiet) {
      return require(`@/assets/img/objectives/header/${wantedDiet.key}.jpg`);
    },
  },
  components: { PleaseWait, SubscriptionBtn, Level },
};
</script>

<style lang="scss">
.premium-choices {
  img {
    max-height: 60px;
    max-width: 130px;
  }

  .previous-cost {
    color: $op-color-red;
    text-decoration: line-through;
  }

  @media (min-width: $op-page-column-width-lg) {
    .premium-details {
      text-align: left;
    }
  }

  h3 {
    width: 100%;
    margin-top: 0px;
    margin-bottom: 20px;
  }
  .premium-subscription h3,
  .premium-subscription .btn {
    background-color: $op-color-subscription-premium !important;
    &:hover {
      background-color: lighten($op-color-subscription-premium, 10%) !important;
    }
    color: white !important;
  }
  .default-subscription h3,
  .default-subscription .btn {
    background-color: $op-color-subscription-free !important;
    &:hover {
      background-color: lighten($op-color-subscription-free, 10%) !important;
    }
  }

  .subscription-column {
    vertical-align: top;
    margin: 0px;
    text-align: center;

    @media (max-width: $op-page-column-width-lg) and (min-width: $op-page-column-width-md) {
      width: 75%;
      margin: auto;
      margin-top: 20px;
    }
    @media (max-width: $op-page-column-width-md) {
      margin-top: 20px;
      width: 100%;
    }
    @media (min-width: $op-page-column-width-lg) {
      width: 45%;
      display: table-cell;
      border: 1px solid $op-color-border;
      border-radius: $op-radius-md;
    }

    .row {
      margin-bottom: 10px;
      min-height: 60px;
    }
    .column-content {
      padding: 10px;
    }
  }

  @media (max-width: $op-page-column-width-lg) {
    .subscription-tab {
      border: 1px solid $op-color-border;
      border-radius: $op-radius-md;
    }
  }

  @media (min-width: $op-page-column-width-lg) {
    #subscription-table {
      display: table;
      margin-top: 10px;
      width: 100%;
      border-spacing: 20px 0px;
    }

    .mono-choice {
      padding-left: 150px;
      padding-right: 150px;
    }
  }

  .premium-diet-activated {
    b {
      font-size: $op-font-xl;
    }
    .unactivated-diet {
      text-decoration: line-through;
      font-weight: bold;
      color: $op-color-alert-danger;
      font-size: $op-font-xl;
      margin: 0px;
    }
  }
  .free-option-without-diet {
    b {
      font-size: $op-font-md;
    }
  }

  .btn {
    margin-top: 20px;
    width: 80%;
    height: 60px;
  }
  .default-subscription .btn {
    font-size: $op-font-lg;
    font-weight: bold;
  }
  .premium-subscription .btn {
    font-size: $op-font-lg;
  }

  .premium-choice-advice {
    margin-top: 20px;
    font-size: $op-font-lg;
  }
}
</style>
