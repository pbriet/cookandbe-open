<template>
  <div id="permission-error-page" :class="isLoggedIn ? 'op-page' : 'op-page-public'">
    <div class="op-page-content" :class="!isLoggedIn ? 'container' : ''">
      <h1>Restriction d'accès</h1>

      <div>
        <p>Vous n'avez pas le niveau de permission suffisant pour effectuer cette action.</p>
        <p>Pour plus d'informations, merci de contacter notre service technique.</p>
      </div>

      <BackButton class="toolbar" :defaultHref="{ name: 'UserHome' }" :nbStepsBack="2">Retour</BackButton><br />
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import BackButton from "@/components/interface/BackButton.vue";

export default {
  name: "PermissionDenied",
  computed: {
    ...mapGetters({
      isLoggedIn: "user/isLoggedIn",
    }),
  },
  components: { BackButton },
};
</script>

<style scoped lang="scss">
#permission-denied-page {
  .toolbar {
    clear: both;
    float: right;
  }
}
</style>
