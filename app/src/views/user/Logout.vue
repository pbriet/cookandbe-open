<template>
  <div></div>
</template>

<script>
import {
  LOGOUT_REDIRECT_URL,
} from "@/config.js";

/*
 * View for signin page
 */
export default {
  name: "Logout",
  created () {
    this.$store.commit("user/logout");
    window.location = LOGOUT_REDIRECT_URL;
  }
};
</script>


