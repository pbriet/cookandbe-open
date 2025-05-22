<template>
  <div id="op-main-footer">
    <div id="op-main-footer-content" class="container">
      <div>
        <ul class="mb-0">
          <li v-if="ENABLE_CONTACT">
            <a :href="WWW_HOST + '/contact'">Nous contacter</a>
          </li>
          <li v-if="!APP_ONLY">
            <a href="https://www.facebook.com/cookandbe" target="_blank">Facebook</a>
          </li>
          <li v-if="!APP_ONLY">
            <a href="https://twitter.com/cookandbe" target="_blank">Twitter</a>
          </li>
          <li v-if="ENABLE_LEGAL">
            <a :href="WWW_HOST + '/legal/#mentions'">Mentions légales</a>
          </li>
          <li v-if="ENABLE_LEGAL">
            <a :href="WWW_HOST + '/legal/#conditions'">Conditions générales</a>
          </li>
          <li v-if="ENABLE_LEGAL">
            <a :href="WWW_HOST + '/legal/#privacy'">Vie privée</a>
          </li>
          <li v-if="ENABLE_LEGAL">
            <a :href="WWW_HOST + '/legal/#credits'">Crédits</a>
          </li>
          <li v-if="!APP_ONLY">
            <a :href="WWW_HOST + '/nutrition'">Nutrition</a>
          </li>
          <li v-if="ENABLE_PUBLIC_PAYMENT">
            <a :href="WWW_HOST + '/tariffs'">Tarifs</a>
          </li>
          <li v-if="!APP_ONLY">
            <a :href="WWW_HOST + '/recettes/'">Recettes</a>
          </li>
        </ul>
        <div id="copyright">
          &copy;
          <span v-if="ENABLE_LEGAL">{{ APP_BRAND_NAME }}</span>
          <span v-else>Tous droits réservés</span>
          {{ new Date().getFullYear() }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  ENABLE_CONTACT,
  APP_ONLY,
  APP_BRAND_NAME,
  ENABLE_PUBLIC_PAYMENT,
  ENABLE_LEGAL,
  WWW_HOST,
} from "@/config.js";

export default {
  name: "Footer",
  props: [],
  data: () => ({
    ENABLE_CONTACT,
    ENABLE_LEGAL,
    ENABLE_PUBLIC_PAYMENT,
    APP_ONLY,
    APP_BRAND_NAME,
    WWW_HOST,
  }),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss">
#op-main-footer {
  background-color: $op-color-footer-background;
  border-top: 1px solid $op-color-footer-border;
  clear: both;
  position: relative;
  color: $op-color-footer-font;

  #op-main-footer-content {
    margin: auto;
    margin-top: 20px;
    padding-bottom: 15px;
    min-height: 45px;
  }

  #op-main-footer-content > div {
    &:after {
      @extend .clearfix;
    }
    @media (max-width: $bootstrap-xs-max) {
      text-align: center;
    }
  }

  ul {
    display: inline-block;
    list-style-type: none;
    padding: 0;

    li {
      display: inline-block;

      @media (max-width: $bootstrap-xs-max) {
        width: 100%;
        padding: 10px;
      }
      @media (min-width: $bootstrap-sm-min) {
        margin-right: 19px;
      }

      a {
        color: rgba(0, 0, 0, 0.5);
        font-size: $op-font-md;
        text-decoration: none;

        &:hover {
          color: black;
        }
      }
    }
  }
  #copyright {
    @media (max-width: $bootstrap-xs-max) {
      text-align: center;
      padding-top: 15px;
    }
    @media (min-width: $bootstrap-sm-min) {
      float: right;
    }
  }
}

@media print {
  #op-main-footer {
    display: none;
  }
}
</style>
