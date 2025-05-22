<template>
  <div id="critical-error-page" :class="isLoggedIn ? 'op-page' : 'op-page-public'">
    <div class="op-page-content container op-container">
      <h4>
        <i class="op-icon-dxxl">
          <FontAwesomeIcon :icon="['fas', 'map-marker-alt']" />
        </i>
        Désolé, cette page n'existe pas ou plus.
      </h4>
      <div class="op-font-md">Pour nous aider, merci d'indiquer comment vous êtes arrivés sur cette page :</div>

      <div id="critical-error-uservoice-embed"></div>

      <button type="button" class="btn btn-danger" @click="moveToHome">Revenir à l'accueil</button>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapMutations } from "vuex";

export default {
  name: "NoSuchPage",
  props: [],
  data: () => ({}),
  mounted() {
    if (window.UserVoice) {
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

    this.set404();
  },
  computed: {
    ...mapGetters({
      isLoggedIn: "user/isLoggedIn",
    }),
  },
  methods: {
    ...mapMutations({
      set404: "meta/set404",
    }),
    moveToHome() {
      this.$router.push("/");
    },
  },
  components: {},
};
</script>

<style scoped lang="scss"></style>
