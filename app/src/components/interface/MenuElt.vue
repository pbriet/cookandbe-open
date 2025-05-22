<template>
  <li class="menu-elt w-100 d-relative" v-if="displayOn">
    <router-link :to="{ name: to }" class="nav-link flex" :class="{ active: isActive, static: isStatic }">
      <div @click="onClick" class="flex">
        <div class="menu-elt-icon">
          <FontAwesomeIcon :icon="['fas', icon]" />
        </div>
        <div class="menu-elt-text">
          <span class="d-none d-md-block">{{ caption }}</span>
          <span class="d-md-none" v-if="shortCaption">{{ shortCaption }}</span>
          <span class="d-md-none" v-if="!shortCaption">{{ caption }}</span>
        </div>
        <div class="menu-elt-badge" v-if="nbNotifications">
          <span class="badge rounded-pill" v-if="nbNotifications > 0">{{ nbNotifications }}</span>
          <span
            class="badge rounded-pill"
            v-if="nbNotifications < 0"
            style="padding-left: 7px !important; padding-right: 7px !important"
            >!</span
          >
        </div>
      </div>
    </router-link>
  </li>
</template>

<script>
/*
 * This component adds an element in the menu.
 * This element is only displayed if a boolean is set
 *
 * It is displayed as being "selected" if the current path
 * matches props.to or props.matchRegexp
 */
export default {
  name: "MenuElt",
  props: [
    "onClick",
    "displayOn",
    "isStatic",
    "to",
    "icon",
    "caption",
    "shortCaption",
    "nbNotifications",
    "matchRegexp",
  ],
  data: () => ({}),
  computed: {
    isActive() {
      return this.matchRegexp && this.$route.path.match(this.matchRegexp);
    },
  },
};
</script>

<style scoped lang="scss">
li {
  text-align: left;
  display: block;

  a {
    color: #777777;
    width: 100%;
    position: relative;
    display: table;

    &:focus,
    &:hover {
      color: #333333;
      text-decoration: none;
    }

    &.active:not(.static),
    &.router-link-active:not(.static) {
      background-color: rgba(0, 0, 0, 0);
      color: $op-color-lime !important;
    }
  }

  .menu-elt-icon {
    text-align: center;
    padding-right: 10px;
    width: 65px;
    display: table-cell;
    vertical-align: middle;
    font-size: $op-font-dmd;
  }

  .menu-elt-text {
    display: table-cell;
    vertical-align: middle;
    @extend .op-font-quicksand;
    font-size: $op-font-lg;
  }

  .menu-elt-badge {
    display: flex;
    flex-direction: row;
    align-items: center;
    position: absolute;
    bottom: 0;
    top: 0;
    right: 6px;
  }
}

a.static {
  &:focus,
  &:hover {
    color: inherit;
    cursor: default;
  }
}
</style>
