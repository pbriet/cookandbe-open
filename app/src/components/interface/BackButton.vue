<template>
  <button type="button" id="back-to-config" class="btn btn-secondary" @click="moveBack">
    <slot></slot>
  </button>
</template>

<script>
import { goBack } from "@/router/index.js";

/*
 * This component add a button "back" to previous page
 */
export default {
  name: "BackButton",
  props: ["defaultHref", "forcedHref", "hasCallback", "forcedCallback", "nbStepsBack", "likeNavigatorBack"],
  methods: {
    moveBack() {
      if (this.likeNavigatorBack) {
        this.$router.go(-1);
        return;
      }
      if (this.forcedHref) {
        this.$router.push(this.forcedHref);
      } else if (this.hasCallback) {
        this.forcedCallback();
      } else {
        goBack(this.defaultHref, this.nbStepsBack);
      }
    },
  },
};
</script>
