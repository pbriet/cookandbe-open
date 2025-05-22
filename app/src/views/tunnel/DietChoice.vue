<template>
  <div id="op-diet-choice-page" class="op-page-public">
    <div class="op-page-title container">
      <div v-if="!diet.selected">
        <h1>Choix de l'alimentation</h1>
      </div>
      <div v-if="diet.selected && diet.selected.hasDiagnostic && !diagnosticResults">
        <h1>{{ diet.selected.title }}</h1>
      </div>
      <div v-if="diet.selected && diagnosticResults">
        <h1>Notre diagnostic</h1>
        <p>{{ diet.selected.title }}</p>
      </div>
    </div>
    <ConfigProgression v-if="ENABLE_DIET_CHOICE_AT_LOGIN"/>
    <div class="op-page-content container">
      <PleaseWait v-if="inProgress" />

      <div v-if="!inProgress">
        <div v-if="!diet.selected">
          <!-- No selected diet -->
          <DietSelector
            :diets="diets"
            v-model:selectedDiet="diet.preselected"
            :subscriptionLevelLimit="currentSubscriptionLevel"
          />
          <div class="diet-choice-btns op-vs">
            <button class="btn btn-success fright" @click="validSelection" v-if="diet.preselected">Sélectionner</button>
            <BackButton class="fright" :hasCallback="true" :forcedCallback="unselectDiet" v-if="diet.preselected">
              Retour
            </BackButton>
          </div>
        </div>

        <div v-if="diet.selected && diet.selected.hasDiagnostic && !diagnosticResults" id="diagnose-section">
          <!-- Diagnostic not filled -->
          <Diagnose
            :diet="diet"
            :submitDiagnostic="submitDiagnostic"
            :errorMessage="errorMessage"
            v-model:questions="questions"
            v-model:profile="profile"
          />
        </div>

        <div v-if="diet.selected && diagnosticResults">
          <!-- Diagnostic results -->
          <DiagnosticResults
            :diet="diet"
            :diagnosticResults="diagnosticResults"
            :showPremiumSelection="showPremiumSelection"
            :finalizeDietSelectionNoPayment="redirectToNextPage"
          />
        </div>
      </div>
    </div>
    <ConfigToolbar v-if="ENABLE_DIET_CHOICE_AT_LOGIN"/>
  </div>
</template>

<script>
import { BASE_URL } from "@/config.js";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import BackButton from "@/components/interface/BackButton.vue";
import DietSelector from "@/components/objective/DietSelector.vue";
import Diagnose from "@/components/objective/Diagnose.vue";
import DiagnosticResults from "@/components/objective/DiagnosticResults.vue";
import ConfigProgression from "@/components/config/ConfigProgression.vue";
import ConfigToolbar from "@/components/config/ConfigToolbar.vue";
import { ENABLE_DIET_CHOICE_AT_LOGIN, ENABLE_PUBLIC_PAYMENT, ENABLE_DIET_DIAGNOSIS_RESULTS } from '@/config.js';
import API from "@/api.js";
import { previousUrl } from "@/router/index.js";
import { mapGetters } from "vuex";

export default {
  name: "DietChoice",
  props: [],
  data() {
    return {
      diet: { preselected: null, selected: null }, // Diet which has been selected (default : null)
      diagnosticResults: null, // If diagnostic, what is its results (default : null)
      showPremiumSelection: false,
      inProgress: false,
      errorMessage: null,
      questions: {}, // Questions asked
      profile: {},
      ENABLE_DIET_CHOICE_AT_LOGIN,
      ENABLE_PUBLIC_PAYMENT,
      forceRoute: false
    };
  },
  mounted() {
    if (this.mainProfile) this.profile = this.mainProfile;
    if (this.$route.params.diet) {
      this.diet.preselected = this.diet.selected = this.dietByKey(this.$route.params.diet);
      this.validSelection();
    }
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
      user: "user/get",
      diets: "diet/getDiets",
      dietByKey: "diet/dietByKey",
      mainProfile: "profile/getMainProfile",
      configMode: "configStage/configMode"
    }),
    currentSubscriptionLevel() {
      return this.user.subscriptionLevel;
    },
    /*
     * Returns true if we need to show/redirect the user a premium selection
     */
    requiresPremiumSelection() {
      if (!ENABLE_PUBLIC_PAYMENT) {
        return false;
      }
      const diet = this.diet.preselected;
      const currentSubscriptionLevel = this.user.subscriptionLevel;

      // Free diet / Free account
      // Redirect to premiumSelection to show the freedom option
      if (currentSubscriptionLevel === 0 && diet.minSubscriptionLevel === 0) {
        return true;
      }

      // User has a subscription and it's high enough
      if (currentSubscriptionLevel > 0 && diet.minSubscriptionLevel <= currentSubscriptionLevel) {
        return false;
      }
      return true;
    },
  },
  watch: {
    mainProfile(newProfile, oldProfile) {
      if (newProfile && !oldProfile) {
        this.profile = newProfile;
      }
    },
  },
  methods: {
    /*
     * Ok, let's go to the next page !
     * - Diagnostic if this diet requires a diagnostic
     * - To myAccount if there is not diagnostic and current subscriptionLevel is high enough
     * - Else : to PremiumChoice
     */
    async validSelection() {
      if (this.diet.preselected.hasDiagnostic) {
        this.diet.selected = this.diet.preselected;
        // Diagnostic : will automatically switch to diagnose mode thanks to v-if
        return;
      }
      this.inProgress = true;

      // No diagnostic : active the objective, and redirects to the correct page
      await this.$store.dispatch("user/activateObjective", { objective: this.diet.preselected, parameters: {} });
      // Reload user to get objectives updated
      await this.$store.dispatch("user/load");
      if (this.requiresPremiumSelection) {
        // No diagnostic and requires payment OR is a free diet,
        // Redirects to premiumSelection
        this.$router.push({ name: "PremiumChoice" });
        return;
      }
      // Non-free diet, and user has already paid.
      // Redirect to myAccount (or config completion)
      this.redirectToNextPage()
    },
    /*
     * Submit the diagnostic form to the server, and retrieve the results
     */
    async submitDiagnostic() {
      this.inProgress = true;
      this.errorMessage = "";
      // Update profile first
      this.profile.userId = this.userId;
      await API.profile.update(this.userId, this.profile.id, this.profile);
      this.$store.dispatch("profile/update");
      // Then ask for diagnostic
      const data = await API.user.diagnose(this.userId, this.diet.selected.id, {
        arguments: this.questions,
        autoSelect: true,
      });
      // Reload user to get objectives updated
      await this.$store.dispatch("user/load");
      if (data.status === "error") {
        this.errorMessage = data.error;
      } else {
        if (!ENABLE_DIET_DIAGNOSIS_RESULTS) {
          // No display of diagnosis results. Going directly to next step
          // Note : Diet is automatically selected when asking diagnosis
          this.forceRoute = true;
          this.redirectToNextPage()
        } else {
          this.diagnosticResults = data.content;
        }
      }
      this.inProgress = false;

      this.showPremiumSelection = this.requiresPremiumSelection;
    },
    redirectToNextPage() {
      this.$store.dispatch("configStage/redirectAfterSubscriptionModification");
    },
    unselectDiet() {
      this.diet.preselected = null;
    },
  },
  /*
   * Overring back button
   * WARNING: this method has a limit. You cannot come from a page and return to the same page !
   */
  beforeRouteLeave(to, from, next) {
    if (!this.configMode || this.forceRoute) {
      // No blocking if not in tunnel mode | or if forcing
      next();
    }
    const nextUrl = BASE_URL + to.fullPath;
    if (nextUrl != previousUrl()) {
      // This is not going back
      return;
    }
    if (!this.diet.preselected) {
      return;
    }
    if (this.diagnosticResults) {
      this.diagnosticResults = null;
      return false;
    }
    if (this.diet.selected) {
      this.diet.selected = null;
      return false;
    }
    this.diet.preselected = null;
    return false;
  },
  components: { PleaseWait, BackButton, DietSelector, Diagnose, DiagnosticResults, ConfigToolbar, ConfigProgression },
};
</script>

<style lang="scss">
#op-diet-choice-page {
  .diet-choice-btns {
    margin: auto;
    clear: both;
    display: block;
    text-align: center;
    .btn {
      margin-right: 10px;
      width: 130px;
      font-size: $op-font-xl;
    }
  }
}

#op-diagnose {
  table {
    margin-top: 20px;
    margin-bottom: 40px;
    td {
      padding: 5px;
      border: solid 1px $op-color-grey-dark;
      font-size: $op-font-md;
      font-weight: bold;
      &:hover {
        cursor: inherit;
      }
    }
    td:first-child {
      width: 100px;
    }
  }

  .diagnose-section {
    @extend .op-vs-10;

    .diagnose-text {
      text-align: justify;
    }

    @media (max-width: $bootstrap-xxs-max) {
      .diagnose-icon {
        @include op-icon-dmd;
        width: 100%;
        text-align: center;
        margin: 10px;
      }
    }
    @media (min-width: $bootstrap-xs-min) {
      display: table;

      .diagnose-text {
        display: table-cell;
        vertical-align: top;
      }

      .diagnose-icon {
        @include op-icon-dmd;
        padding: 10px 35px;
        display: table-cell;
      }
    }
  }
}

#diagnose-section {
  .btn {
    width: 100%;
  }
  .alert {
    margin-bottom: 20px;
  }
}
</style>
