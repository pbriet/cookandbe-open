<template>
  <teleport to="head">
    <meta name="robots" :content="metaRobotsInfos" />
    <meta name="description" :content="metaDescription" />
    <meta name="keywords" :content="metaKeywords" />
    <meta name="prerender-status-code" :content="metaStatusCode" />

    <meta property="og:site_name" :content="APP_BRAND_NAME" />
    <meta property="og:url" :content="window.location.href" />
    <meta property="og:title" :content="metaOgTitle" />
    <meta property="og:description" :content="metaDescription" />
    <meta property="og:type" :content="metaOgType" />
    <meta property="og:image" :content="metaOgImage" />
    <meta property="og:image:width" :content="metaOgImageWidth" />
    <meta property="og:image:height" :content="metaOgImageHeight" />

    <title>{{ metaTitle }}</title>

  </teleport>

  <div id="please-wait-main" v-show="!loaded">
    <img
      :src="'/' + IMG_BRAND + '/img/logo1.jpg'"
      alt="Veuillez patienter"
      id="please-wait-logo"
      style="width: 100%; max-width: 400px"
      :class="ENABLE_LOGO ? 'd-inline-block' : 'd-none'"
    />
    <br />
    <img src="~@/assets/img/please-wait.gif" width="150" />
    Veuillez patienter...
  </div>

  <!-- Required for facebook -->
  <div id="fb-root"></div>

  <!-- Premium modal -->
  <PremiumModal />

  <!-- Maintenance popup -->
  <MaintenanceModal />

  <!-- Login modal -->
  <Dialog
    id="login-popup"
    class="info in"
    :open="loginPopupOpen"
    :closeBtn="true"
    :onClose="hideLogin"
    focusElt="#login-email-input"
  >
    <div id="login-panel">
      <Login />
    </div>
  </Dialog>

  <!-- CGU -->
  <Dialog :open="cgvOpen" :closeBtn="true" :onClose="hideCgv">
    <Cgv />
  </Dialog>

  <!-- Banner -->
  <Banner :banner="banner" />

  <!-- Top menu -->
  <MainMenu :onLogin="showLogin" v-if="loaded" />

  <!-- Page content -->
  <div id="op-body" class="full-w full-h" v-if="loaded">
    <router-view v-if="!cookiesDisabled" />
    <CookiesAlert v-if="cookiesDisabled" />
  </div>

  <Footer v-if="loaded && !isLoggedIn" />

  <!-- Uservoice -->
  <UserVoice :show="loaded" />
</template>

<script>
import "jquery";
import "@popperjs/core";
import "bootstrap";
import { mapGetters, mapMutations } from "vuex";
import { ENABLE_LOGO, APP_BRAND_NAME, IMG_BRAND } from "@/config.js";
import API from "@/api.js";

import Banner from "@/components/interface/Banner.vue";
import CookiesAlert from "@/components/interface/CookiesAlert.vue";
import Dialog from "@/components/interface/Dialog.vue";
import MaintenanceModal from "@/components/interface/MaintenanceModal.vue";
import PremiumModal from "@/components/interface/PremiumModal.vue";
import Footer from "@/components/interface/Footer.vue";
import MainMenu from "@/components/main_menu/MainMenu.vue";
import Cgv from "@/components/corp/legal/Cgv.vue";
import Login from "@/components/user/Login.vue";
import UserVoice from "@/components/main_menu/UserVoice.vue";

export default {
  name: "App",
  data: () => ({
    loaded: false,
    ENABLE_LOGO,
    APP_BRAND_NAME,
    IMG_BRAND,
    window,
  }),
  mounted() {
    // The following initialize the CSRF token with a first (dummy) GET request
    API.init();
    this.$store.dispatch("services/init").then(() => {
      this.loaded = true;
      if (this.isLoggedIn && this.user.justExpired) {
        this.$router.push({ name: "Expired" });
      }
    });

    if (typeof window.ga == "undefined") {
      // Required for prerender, who blocks in purpose the load of ganalytics
      this.disableGoogleAnalytics();
    }
    if (this.ENABLE_GOOGLE_ANALYTICS) {
      window.ga("create", "UA-53112251-1", "auto");
    }
  },
  computed: {
    ...mapGetters({
      user: "user/get",
      isLoggedIn: "user/isLoggedIn",
      loginPopupOpen: "dialog/loginPopup",
      cgvOpen: "dialog/signupTerms",
      metaTitle: "meta/title",
      metaRobotsInfos: "meta/robotsInfos",
      metaDescription: "meta/description",
      metaKeywords: "meta/keywords",
      metaStatusCode: "meta/statusCode",
      metaOgTitle: "meta/ogTitle",
      metaOgType: "meta/ogType",
      metaOgImage: "meta/ogImage",
      metaOgImageWidth: "meta/ogImageWidth",
      metaOgImageHeight: "meta/ogImageHeight",
      ENABLE_GOOGLE_ANALYTICS: "analytics/ENABLE_GOOGLE_ANALYTICS",
    }),
    banner() {
      return this.$route.meta.banner ?? "default";
    },
    cookiesDisabled() {
      return !navigator.cookieEnabled;
    },
  },
  methods: {
    ...mapMutations({
      disableGoogleAnalytics: "analytics/disableGoogleAnalytics",
    }),
    showLogin() {
      this.$store.commit("dialog/showLoginPopup");
    },
    hideLogin() {
      this.$store.commit("dialog/hideLoginPopup");
    },
    hideCgv() {
      this.$store.commit("dialog/hideSignupTerms");
    },
  },
  components: {
    Banner,
    Dialog,
    MainMenu,
    Login,
    UserVoice,
    MaintenanceModal,
    Cgv,
    CookiesAlert,
    PremiumModal,
    Footer,
  },
};
</script>

<style lang="scss">
@import "@/assets/css/global.scss";

#nav {
  padding: 30px;

  a {
    font-weight: bold;
    color: #2c3e50;
  }
}

@media (min-width: $op-page-column-width-md) {
  #login-popup {
    .modal-dialog {
      width: 70%;
      max-width: 800px;
    }
  }
}

#please_wait_modal {
  z-index: 3000;
  padding-top: 200px;
}

#please-wait-main {
  position: absolute;
  margin-top: 50px;
  width: 100%;
  text-align: center;
  background-color: white;
  padding: 20px;
  z-index: 1000;
}

#op-body {
  &:after {
    @extend .clearfix;
  }
  background-color: $op-color-margin;
  min-height: 200px;
}

#alert-no-cookies {
  background-color: $op-color-yellow-logo;
  border: none;
  color: black;
  font-size: 18px;
  td {
    padding-right: 20px;
    vertical-align: middle;
  }
}

#login-panel {
  display: block;

  .signup-mode {
    margin-bottom: 20px;
  }
  @media (max-width: $bootstrap-sm-max) {
    .connect-mode:nth-of-type(1) {
      margin-bottom: 30px;
    }
  }

  .connect-choices {
    .connect-caption {
      margin-bottom: 5px;
    }
  }

  form > div:last-child > div {
    padding: 0;
  }

  @media (min-width: $bootstrap-md-min) {
    form > div:last-child {
      padding: 0;
    }
  }

  .facebook-connect-btn {
    @media (min-width: $bootstrap-md-min) {
      width: 300px;
    }
  }
}

@import "@/components/objective/objective.scss";
</style>
