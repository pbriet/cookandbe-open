<template>
  <div class="full-h">
    <nav
      id="user-menu"
      role="navigation"
      class="navbar navbar-default navbar-light absolute-menu-top op-menu navbar-expand-sm"
    >
      <div class="navbar-header">
        <button
          id="user-menu-top-toggle"
          type="button"
          class="navbar-toggler fright collapsed"
          data-bs-toggle="collapse"
          data-bs-target="#user-menu-top"
        >
          <span class="visually-hidden-focusable">Toggle navigation</span>
          <span class="visitor-menu-label">Menu <FontAwesomeIcon :icon="['fas', 'bars']" /></span>
        </button>
        <ul class="hvm-none hvp-none d-inline-block" v-if="ENABLE_LOGO">
          <li :class="{ active: isActive }">
            <router-link class="navbar-brand d-block" :to="{ name: 'UserHome' }">
              <span @click="collapse">
                <img :src="'/' + IMG_BRAND + '/img/logo-black-wide.png'" />
              </span>
            </router-link>
          </li>
        </ul>
        <ul class="nav navbar-right" v-show="!user"></ul>
      </div>
      <!-- User buttons toggled on mobile -->
      <nav ref="toggler" id="user-menu-top" class="navbar-collapse collapse">
        <!-- Tutorial empty modal -->
        <Dialog id="tutorial-empty-modal" :open="tutorialPopupOpen"></Dialog>
        <div id="user-menu-login" class="d-flex full-w hp-sm vp-md">
          <router-link :to="{ name: 'Settings' }" class="d-flex flex-grow-1">
            <span @click="collapse" class="d-flex">
              <span class="user-menu-icon hp-md"><FontAwesomeIcon :icon="['fas', 'user']" /></span>Bonjour
              {{ user.name }} !
            </span>
          </router-link>
          <a @click="logout" class="op-clickable user-menu-icon"><FontAwesomeIcon :icon="['fas', 'power-off']" /></a>
        </div>
        <ul class="nav navbar-nav">
          <MenuElt to="UserHome" icon="home" caption="Accueil" :displayOn="user" :onClick="collapse" />
          <MenuElt
            to="Calendar"
            matchRegexp="^/(calendar|day|day_planner)"
            id="menu-elt-calendar"
            icon="utensils"
            :nbNotifications="planificationStatus && planificationStatus.plannedTo === null ? -1 : 0"
            caption="Idées repas"
            :displayOn="user"
            :onClick="collapse"
          />
          <MenuElt
            to="Shopping"
            id="menu-elt-shopping-list"
            icon="shopping-basket"
            :nbNotifications="availableDays.plannedDates && availableDays.plannedDates.length"
            caption="Liste de courses"
            shortCaption="Liste"
            :displayOn="user"
            :onClick="collapse"
          />
          <MenuElt
            to="Cookbook"
            matchRegexp="^/(carnet|recettes/\d+/edit)"
            icon="book"
            caption="Mes recettes"
            shortCaption="Recettes"
            :displayOn="user"
            :onClick="collapse"
          />
          <MenuElt
            to="MyAccount"
            icon="apple-alt"
            caption="Alimentation"
            v-if="user && ENABLE_DIET_CHOICE"
            :displayOn="user"
            :onClick="collapse"
          />
          <MenuElt
            to="DiscussionList"
            icon="comments"
            :nbNotifications="unreadDiscussions"
            caption="Nutritionniste"
            v-if="shouldDisplayDiscussions"
            :displayOn="user"
            :onClick="collapse"
          />
          <MenuElt
            id="menu-elt-config"
            to="Config"
            icon="cog"
            :nbNotifications="configStats.nbIncomplete"
            caption="Configuration"
            :displayOn="user"
            :onClick="collapse"
          />
        </ul>
        <div id="user-menu-footer" class="block full-w hp-sm vp-md">
          <ul class="full-w hvm-none hvp-none">
            <li class="text-center" v-if="ENABLE_CONTACT">
              <a @click="collapse" :href="WWW_HOST + '/contact'">Nous contacter</a>
            </li>
            <li class="text-center" v-if="ENABLE_LEGAL">
              <a @click="collapse" :href="WWW_HOST + '/legal/#mentions'">Mentions légales</a>
            </li>
            <li class="text-center" v-if="ENABLE_LEGAL">
              <a @click="collapse" :href="WWW_HOST + '/legal/#conditions'">Conditions générales</a>
            </li>
          </ul>
          <div id="copyright">
            &copy;
            <span v-if="ENABLE_LEGAL">{{ APP_BRAND_NAME }}</span>
            <span v-else>Tous droits réservés</span>
            {{ new Date().getFullYear() }}
          </div>
        </div>
      </nav>
    </nav>
  </div>
</template>

<script>
import { Collapse } from "bootstrap";
import { mapGetters } from "vuex";
import {
  APP_BRAND_NAME,
  ENABLE_PUBLIC_PAGES,
  ENABLE_CONTACT,
  ENABLE_DIET_CHOICE,
  ENABLE_DISCUSSION,
  IMG_BRAND,
  WWW_HOST,
  LOGOUT_REDIRECT_URL,
  ENABLE_LEGAL,
} from "@/config.js";
import MenuElt from "@/components/interface/MenuElt.vue";
import Dialog from "@/components/interface/Dialog.vue";

export default {
  name: "MainMenuUser",
  props: ["ENABLE_LOGO"],
  data: () => ({
    APP_BRAND_NAME,
    ENABLE_PUBLIC_PAGES,
    ENABLE_CONTACT,
    ENABLE_DIET_CHOICE,
    IMG_BRAND,
    WWW_HOST,
    ENABLE_LEGAL,
    currentYear: new Date().getFullYear(),
    menu: null,
  }),
  mounted() {
    this.menu = new Collapse(this.$refs.toggler, {
      toggle: false,
    });
  },
  computed: {
    ...mapGetters({
      user: "user/get",
      planificationStatus: "planning/getPlanificationStatus",
      availableDays: "shopping/getAvailableDays",
      configStats: "configStage/getStats",
      unreadDiscussions: "discussion/nbUnread",
      tutorialPopupOpen: "dialog/tutorialOverlay",
    }),
    isActive() {
      return this.$route.name == "UserHome";
    },
    shouldDisplayDiscussions() {
      if (!ENABLE_DISCUSSION) {
        return false;
      }
      if (!this.user || this.user.fromBiodyManager) {
        return false;
      }
      return true;
    },
  },
  methods: {
    collapse() {
      this.menu.hide();
    },
    async logout() {
      this.$store.commit("user/logout");
      window.location = LOGOUT_REDIRECT_URL;
    },
  },
  components: {
    MenuElt,
    Dialog,
  },
};
</script>

<style scoped lang="scss">
@import "./common";
$menu-fade: 0.95;
$menu-shadow: 0.25;

.navbar {
  padding-top: 0;
  @media (max-width: $bootstrap-xs-max) {
    padding-bottom: 0;
  }
}

.navbar-brand {
  padding-bottom: 0;
  margin-right: auto;
}

@media (max-width: $bootstrap-xs-max) {
  .navbar-brand {
    height: 51px;
  }
}

.absolute-menu-top {
  width: 100%;
  position: relative;
  box-shadow: 0 0 5px rgba(0, 0, 0, $menu-shadow);
  -webkit-box-shadow: 0 0 5px rgba(0, 0, 0, $menu-shadow);
  -moz-box-shadow: 0 0 5px rgba(0, 0, 0, $menu-shadow);
  background: rgba(255, 255, 255, $menu-fade);
}

@media (min-width: $bootstrap-sm-min) {
  .navbar-expand-sm .navbar-collapse {
    display: block !important;
  }
}

#user-menu {
  border: 0;
  box-shadow: none;
  -webkit-box-shadow: none;
  display: block;
  background-color: rgba($op-color-beige-light, $menu-fade);

  @media (max-width: $bootstrap-xs-max) {
    width: 100%;
  }
  @media (min-width: $bootstrap-sm-min) {
    width: $menu-user-width;
    height: 100%;
    .navbar-toggler {
      display: none;
    }
  }

  .navbar-toggler {
    padding: 5px;
    margin: 10px;
  }
}

#user-menu-login {
  border: 1px solid darken($op-color-beige-light, 10%);
  border-left: 0;
  border-right: 0;

  margin-top: -5px;
  margin-bottom: 0;

  .user-menu-icon {
    line-height: 1.1;
  }
}

#user-menu-footer {
  border-top: 1px solid darken($op-color-beige-light, 10%);
  text-align: center;
  font-size: $op-font-sm;
  color: darken($op-color-beige-light, 30%);

  @media (max-width: $bootstrap-xs-max) {
    @include vm-sm;
  }
  @media (min-width: $bootstrap-sm-min) {
    @include vm-lg;
  }
}

#user-menu-top {
  padding: 0px;
  .nav.navbar-nav {
    margin-top: 5px;
    margin-bottom: 10px;
  }
}
</style>

<style lang="scss">
$menu-user-row-height: 40px;

.navbar-toggler:hover,
.navbar-toggler:focus {
  background-color: #ddd;
}

#user-menu {
  ul {
    .menu-elt {
      height: $menu-user-row-height;
      display: block;
      color: black;
      font-weight: bold;
      vertical-align: middle;

      a {
        padding-left: 5px;
      }
    }
  }
}
</style>
