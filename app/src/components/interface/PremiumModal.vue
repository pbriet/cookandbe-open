<template>
  <Dialog :open="show" id="requires-premium-modal" class="info in" style="z-index: 1041">
    <div class="dialog-title">Cette fonctionnalité est limitée</div>
    <div class="dialog-body">
      <h3>
        Passez en abonnement <b>{{ SUBSCRIPTION_NAMES[1] }}</b> aujourd'hui !
      </h3>
      <div class="op-font-md">
        <p>A partir de 10€/mois, bénéficiez de :</p>
        <ul>
          <li>La possibilité <b>d'imposer des recettes</b> dans vos plannings. Avec rééquilibrage automatique !</li>
          <li><b>Exclusion d'aliments illimitée</b> : autant de goûts que vous le souhaitez</li>
          <li>Possibilité d'ajouter un <b>goûter et/ou une collation</b> dans votre journée équilibrée</li>
        </ul>
      </div>
      <button class="btn btn-success me-2" @click="showDetails">Voir les détails</button>
      <button class="btn btn-secondary" @click="closePremiumModal">Plus tard</button>
    </div>
  </Dialog>
</template>

<script>
import { SUBSCRIPTION_NAMES } from "@/common/static.js";
import Dialog from "@/components/interface/Dialog.vue";
import { mapGetters } from "vuex";

export default {
  name: "PremiumModal",
  props: [],
  data: () => ({
    SUBSCRIPTION_NAMES,
  }),
  computed: {
    ...mapGetters({
      show: "dialog/premiumModal",
    }),
  },
  methods: {
    showDetails() {
      this.closePremiumModal();
      this.$router.push({ name: "PremiumChoice" });
    },
    closePremiumModal() {
      this.$store.commit("dialog/hidePremiumModal");
    },
  },
  components: { Dialog },
};
</script>

<style scoped lang="scss">
#requires-premium-modal {
  ul {
    padding-left: 20px;
  }
  li {
    margin-top: 10px;
  }
}
</style>
