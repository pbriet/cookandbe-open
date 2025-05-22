<template>
  <div id="critical-error-page" :class="isLoggedIn ? 'op-page' : 'op-page-public'">
    <div class="op-page-content container op-container">
      <h4>
        <span class="op-icon-dxxl">
          <FontAwesomeIcon :icon="['far', 'frown']" />
        </span>
        Oh oh ! Quelque chose ne s'est pas passé comme prévu !
      </h4>
      <div class="op-font-lg">Notre équipe technique a été avertie.</div>
      <br />

      <div v-show="!uservoiceDisabled">
        <div class="op-font-md">Pour nous aider, merci d'indiquer comment le bug est arrivé :</div>
        <div id="critical-error-uservoice-embed"></div>
      </div>

      <router-link class="btn btn-danger" :to="{ name: 'SignIn' }">Revenir à l'accueil</router-link>
      <a class="btn btn-secondary d-inline-block ms-3" :href="WWW_HOST + '/contact/'" v-if="uservoiceDisabled && ENABLE_CONTACT"
        >Nous contacter</a
      >
    </div>
  </div>
</template>

<script>
import { ENABLE_CONTACT, WWW_HOST } from "@/config.js";
import { mapGetters } from "vuex";

export default {
  name: "CriticalError",
  mounted() {
    if (!this.uservoiceDisabled) {
      window.UserVoice.push([
        "embed",
        "#critical-error-uservoice-embed",
        {
          mode: "contact",
          accent_color: "#6aba2e",
          contact_title: "",
          screenshot_enabled: false,
        },
      ]);
    }
  },
  data: () => ({ ENABLE_CONTACT, WWW_HOST }),
  computed: {
    ...mapGetters({
      isLoggedIn: "user/isLoggedIn",
    }),
    uservoiceDisabled() {
      return typeof window.UserVoice === "undefined" || window.UserVoice === undefined || window.UserVoice === null;
    },
  },
};
</script>

<style scoped lang="scss"></style>
