<template>
  <div v-bind:class="[isLoggedIn ? 'op-page' : 'op-page-public']">
    <div class="op-page-title container op-container">
      <h1>Impossible de se connecter</h1>
    </div>
    <div class="op-page-content container op-container">
      <p class="op-vs-10 op-font-lg">Les données de connexion sont invalides.</p>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  name: "Wrongtoken",
  computed: {
    ...mapGetters({
      isLoggedIn: "user/isLoggedIn",
    }),
  },
};
</script>
