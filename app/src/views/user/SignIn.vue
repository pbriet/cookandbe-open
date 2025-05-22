<template>
  <div v-bind:class="[isLoggedIn ? 'op-page' : 'op-page-public']">
    <div class="op-page-title container">
      <h1>Identification</h1>
    </div>
    <div class="op-page-content container">
      <div class="alert alert-warning text-center" v-if="warning">
        <h4><FontAwesomeIcon :icon="['fas', 'info-circle']" /> {{ warning.title }}</h4>
        {{ warning.message }}
      </div>
      <Login :resetCode="$route.query.code" :email="$route.query.email" />
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import Login from "@/components/user/Login.vue";

/*
 * View for signin page
 */
export default {
  name: "SignIn",
  computed: {
    ...mapGetters({
      isLoggedIn: "user/isLoggedIn",
    }),
    warning() {
      if (this.$route.params.reason == "expired")
        return {
          title: "Votre session a expiré",
          message: "Entrez vos identifiants pour vous reconnecter.",
        };
      else if (this.$route.params.reason == "required")
        return {
          title: "Vous devez être authentifié pour accéder à cette page",
          message: "Entrez vos identifiants pour vous connecter.",
        };
      else if (this.$route.params.reason == "renewed")
        return {
          title: "Votre mot de passe a bien été réinitialisé",
          message: "Entrez vos identifiants pour vous connecter.",
        };
      return null;
    },
  },
  components: {
    Login,
  },
};
</script>

<style scoped lang="scss">
h1 {
  margin-top: 20px;
  margin-bottom: 10px;
  line-height: 1.1;
}
</style>
