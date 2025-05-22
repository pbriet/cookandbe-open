<template>
  <header
    id="visitor-menu"
    role="navigation"
    class="op-menu navbar-static-top navbar-expand-sm d-print-none full-w"
    v-if="!isLoggedIn"
  >
    <div class="navbar p-0">
      <div class="visitor-menu-container p-0 container">
        <div class="row g-0 full-w">
          <div>
            <div class="navbar-header full-w" v-if="ENABLE_LOGO">
              <router-link class="navbar-brand float-start" @click="collapse" to="/">
                <img :src="'/' + IMG_BRAND + '/img/logo-small-white.png'" />
              </router-link>
              <button
                id="visitor-menu-top-toggle"
                type="button"
                class="navbar-toggler float-end"
                data-bs-toggle="collapse"
                data-bs-target="#visitor-menu-top"
              >
                <span class="visually-hidden-focusable">Toggle navigation</span>
                <span class="visitor-menu-label"
                  >Menu <span class="icon"><FontAwesomeIcon :icon="['fas', 'bars']" size="lg" /> </span
                ></span>
              </button>
            </div>
            <nav id="visitor-menu-top" class="navbar-collapse collapse">
              <ul class="nav navbar-nav" v-if="ENABLE_PUBLIC_PAGES">
                <li><a @click="collapse" :href="WWW_HOST + '/how'">Fonctionnement</a></li>
                <li>
                  <a @click="collapse" :href="WWW_HOST + '/recettes'" class="d-sm-none d-md-inline-block">Recettes</a>
                </li>
                <li>
                  <a @click="collapse" :href="WWW_HOST + '/nutrition'" class="d-sm-none d-md-inline-block">Nutrition</a>
                </li>
                <li><a @click="collapse" :href="WWW_HOST + '/partners'">Partenaires</a></li>
                <li><a @click="collapse" :href="WWW_HOST + '/team'">L'équipe</a></li>
                <li><a @click="collapse" :href="WWW_HOST + '/tariffs'">Tarifs</a></li>
                <li>
                  <a @click="collapse" :href="WWW_HOST + '/marque-blanche'" class="biz-menu-elt d-sm-none d-md-inline-block"
                    >Entreprises</a
                  >
                </li>
              </ul>
              <ul class="nav navbar-nav ms-auto">
                <li>
                  <button type="button" class="btn btn-success menu-top-button" @click="onLogin">Connexion</button>
                </li>
              </ul>
            </nav>
            <span class="clearfix" />
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { mapGetters } from "vuex";
import { ENABLE_LOGO, ENABLE_PUBLIC_PAGES, IMG_BRAND, WWW_HOST } from "@/config.js";

export default {
  name: "MainMenuVisitor",
  props: ["hrefCollapse", "onLogin"],
  data: () => ({
    ENABLE_LOGO,
    ENABLE_PUBLIC_PAGES,
    IMG_BRAND,
    WWW_HOST,
  }),
  computed: {
    ...mapGetters({
      isLoggedIn: "user/isLoggedIn",
    }),
  },
  methods: {
    collapse() {
      this.hrefCollapse("#visitor-menu-top");
    },
  },
};
</script>

<style scoped lang="scss">
@import "./common";

.navbar-static-top {
  z-index: 1000;
}

.menu-top-button {
  margin: 10px;
  float: right;
}

#visitor-menu {
  $visitor-menu-height: 150px;

  position: fixed;
  border: none;
  box-shadow: none;
  margin-bottom: 0px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.65), transparent);

  .visitor-menu-container {
    min-height: $visitor-menu-height;
    align-items: flex-start;
  }

  .navbar-header {
    @media (max-width: $bootstrap-xs-max) {
      overflow-y: auto;
    }

    .visitor-menu-label {
      @media (max-width: $bootstrap-xs-max) {
        font-size: 14px;
        color: white;
        text-transform: uppercase;
      }
      @media (min-width: $bootstrap-sm-min) {
        display: none;
      }
    }

    .navbar-brand {
      padding-left: 0px;
      @media (max-width: $bootstrap-xs-max) {
        padding-left: 10px;
      }
      @media (min-width: $bootstrap-sm-min) {
        margin-left: -5px;
      }
    }

    .navbar-toggler {
      background-color: transparent;
      border: none;
      padding: 14px 15px;
      margin-top: 8px;
      margin-bottom: 8px;
      margin-right: 7px;
      .icon {
        margin-left: 6px;
      }
    }
  }

  .navbar-collapse {
    @media (max-width: $bootstrap-xs-max) {
      padding-top: 14px;
      background-color: rgba($op-color-lime, 0.8);
      text-align: center;
      font-size: 20px;
      margin-bottom: 35px;
    }

    @media (min-width: $bootstrap-sm-min) {
      margin-left: 5px;
      font-size: 14px;
    }

    a {
      font-family: $op-family-quicksand;
      margin-top: 13px;
      @media (max-width: $bootstrap-xs-max) {
        margin-top: 9px;
      }
      display: inline-block;
      padding: 10px;
      color: white;
      background-color: transparent !important;

      &:hover {
        color: yellow;
        text-decoration: none;
      }
      &.biz-menu-elt {
        @media (min-width: $bootstrap-sm-min) {
          font-weight: bold;
        }
        @media (max-width: $bootstrap-xs-max) {
          color: yellow;
        }
        @media (min-width: $bootstrap-lg-min) {
          padding-left: 40px;
        }
      }
    }
  }

  .menu-top-button {
    @media (max-width: $bootstrap-xs-max) {
      float: none;
      display: block;
      margin: auto;
      font-size: 20px;
      margin-bottom: 30px;
      margin-top: 30px;
    }

    @media (min-width: $bootstrap-sm-min) {
      margin-top: 21px;
    }

    background-color: transparent;
    border: 1px solid yellow;
    border-radius: 10px;
    font-family: $op-family-quicksand;

    &:hover {
      background-color: yellow;
      color: black;
    }
  }
}
</style>
