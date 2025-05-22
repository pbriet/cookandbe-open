<template>
  <MainMenuVisitor :hrefCollapse="hrefCollapse" :onLogin="onLogin" />
  <MainMenuPrint />

  <!-- Connected menu -->
  <div id="main-menu" class="d-print-none" v-if="showMainMenu">
    <div class="menu-fixed" v-if="!showEmptyMenu">
      <!-- User menu -->
      <MainMenuUser :ENABLE_LOGO="ENABLE_LOGO" />
    </div>
  </div>

  <!-- Subscription disclaimer -->
  <div role="alert" class="main-menu-alert" v-if="hasDisabledDietAlert">
    <div class="content hp-md vp-md">
      <span class="op-icon-dmd icon">
        <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" />
      </span>
      <div style="display: inline-block">
        <h4>Alimentation désactivée : {{ wantedDiet.title }}</h4>
        <div class="d-none d-ms-block">Merci de prendre un abonnement pour l'activer.</div>
      </div>
      <router-link class="btn btn-secondary" :to="{ name: 'DietChoice' }"> Changer d'alimentation </router-link>
      <router-link class="btn btn-secondary" :to="{ name: 'Expired' }"> S'abonner </router-link>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import MainMenuVisitor from "./MainMenuVisitor.vue";
import MainMenuPrint from "./MainMenuPrint.vue";
import MainMenuUser from "./MainMenuUser.vue";
import { ENABLE_LOGO, ENABLE_PUBLIC_PAYMENT } from "@/config.js";
import $ from "jquery";

const HIDE_EXPIRED_PAGES = ["MyAccount", "PaymentChoice", "Expired", "DietChoice", "PremiumChoice"];

export default {
  name: "MainMenu",
  props: ["onLogin"],
  data: () => ({
    ENABLE_LOGO,
    ENABLE_PUBLIC_PAYMENT,
  }),
  computed: {
    ...mapGetters({
      showMainMenu: "user/isLoggedIn",
      user: "user/get",
    }),
    showEmptyMenu() {
      if (!this.user) {
        return false;
      }

      const url = this.$route.path;
      // Specific pages with no menu
      const emptyUrls = ["/diet_choice", "/premium_choice", "/payment_choice"];
      for (let i = 0; i < emptyUrls.length; i++) {
        if (url.indexOf(emptyUrls[i]) != -1) {
          return true;
        }
      }

      // Configuration progression has no menu
      return this.$route.query["config_completion"];
    },
    wantedDiet() {
      return this.user.wantedObjective;
    },
    hasDisabledDietAlert() {
      if (this.currentlyOnPages(HIDE_EXPIRED_PAGES)) {
        return false;
      }
      if (!this.user) {
        // If no user, there won't be any warning anyway
        return false;
      }
      if (!this.user.freeTrial.consumed) {
        // User has not consumed his free trial yet !
        return false;
      }
      const currentDiet = this.user.objective;
      return currentDiet && this.wantedDiet.key !== currentDiet.key;
    },
  },
  methods: {
    currentlyOnPages(pages) {
      for (let i = 0; i < pages.length; ++i) {
        if (this.$route.name == pages[i]) {
          return true;
        }
      }
      return false;
    },
    hrefCollapse(target) {
      if ($(target + "-toggle").is(":visible")) {
        $(target).collapse("hide");
      }
    },
  },
  components: {
    MainMenuVisitor,
    MainMenuPrint,
    MainMenuUser,
  },
};
</script>

<style scoped lang="scss">
$menu-user-sm-height: 50px;

.menu-fixed {
  position: fixed;
  z-index: 100;
}

#main-menu {
  position: relative;
  height: 100%;

  @media (max-width: $bootstrap-xs-max) {
    width: 100%;
    height: $menu-user-sm-height;

    .menu-fixed {
      width: 100%;
    }
  }
  @media (min-width: $bootstrap-sm-min) {
    width: $menu-user-width;
    height: 100%;

    .menu-fixed {
      height: 100%;
    }
  }
}

.main-menu-alert {
  position: relative;

  @media (min-width: $bootstrap-sm-min) {
    padding-left: $menu-user-width;
  }

  .content {
    width: 100%;
    background-color: $op-color-grey-dark;
    color: white;
  }

  .icon {
    padding: 10px;
  }

  h4 {
    font-weight: bold;
    margin: 0px;
    @media (max-width: $bootstrap-sm-max) {
      font-size: 13px;
      .btn {
        padding: 5px 10px;
        font-size: 12px;
      }
    }
  }

  .btn {
    float: right;
    margin-top: 2px;
    margin-left: 3px;
    margin-right: 3px;
  }

  &:after {
    @extend .clearfix;
  }

  @media (max-width: $bootstrap-sm-max) {
    text-align: center;
    .btn {
      margin: 0 !important;
      float: none;
    }
  }
}
</style>
