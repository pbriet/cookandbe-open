<template>
  <div id="preconfiguration-page" class="op-page-public">
    <div class="op-page-title container">
      <h1>Vos préférences</h1>
    </div>
    <ConfigProgression />
    <div class="op-page-content container">
      <Dialog id="configuration-reset-warning" :open="openDialog" :closeBtn="true">
        <div class="dialog-title">Cette action réinitialisera votre profil</div>
        <div class="dialog-body">
          <p>Les modifications que vous avez déjà effectuées seront annulées.</p>

          <div class="row">
            <div class="col-6 col-sm-3 ms-auto">
              <div class="btn btn-success btn-block" @click="validate(true)">Ok</div>
            </div>
            <div class="col-6 col-sm-3">
              <div class="btn btn-secondary btn-block" @click="openDialog = false">Annuler</div>
            </div>
          </div>
        </div>
      </Dialog>

      <ConfigBudgetProteins v-model:warning="warning" v-model:values="values" :enableTime="true" />

      <div id="lets-go-section" v-if="!inProgress">
        <button class="btn btn-success op-font-xl" :disabled="warning.blocking" @click="validate(false)">
          C'est parti !
        </button>
      </div>

      <PleaseWait v-if="inProgress" caption="Création de votre profil en cours..." />
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import Dialog from "@/components/interface/Dialog.vue";
import PleaseWait from "@/components/interface/PleaseWait.vue";
import ConfigProgression from "@/components/config/ConfigProgression.vue";
import ConfigBudgetProteins from "@/components/config/ConfigBudgetProteins.vue";
import { startTutorial } from "@/tutorial.js";
import API from "@/api.js";

export default {
  name: "Preconfiguration",
  props: [],
  data: () => ({
    openDialog: false,
    inProgress: false,
    warning: {},
    values: {},
  }),
  computed: {
    ...mapGetters({
      userId: "user/id",
      configStats: "configStage/getStats",
    }),
  },
  methods: {
    /*
     * Submit values to the server
     */
    async validate(force) {
      if (!force && this.configStats.nbCompleted > 1) {
        this.openDialog = true;
        return;
      }
      if (force) {
        this.openDialog = false;
      }
      this.inProgress = true;
      await API.user.preconfigure(this.userId, { speed: this.values.speed });
      // Configuration complete !
      this.$router.push({ name: "Calendar" });
      setTimeout(() => {
        startTutorial("menuTutorial");
      }, 500);
      this.inProgress = false;
    },
  },
  beforeRouteLeave(to, from, next) {
    this.$store.dispatch("configStage/complete", { stageName: "other" });
    next();
  },
  components: { Dialog, PleaseWait, ConfigProgression, ConfigBudgetProteins },
};
</script>

<style scoped lang="scss">
#preconfiguration-page {
  #lets-go-section {
    margin-bottom: 20px;

    .btn-success {
      width: 200px;
      margin: auto;
      display: block;
    }
  }
}
</style>
