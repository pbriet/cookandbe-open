<template>
  <div class="btn-toolbar config-toolbar op-page-content" :class="{ container: configMode }" role="toolbar">
    <div class="btn-group">
      <router-link class="btn btn-success" :to="{ name: 'Config' }" v-if="!configMode">Terminer</router-link>
      <button class="btn btn-success" @click="goToNextStep" v-if="configMode">Suivant</button>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";

export default {
  name: "ConfigToolbar",
  computed: {
    ...mapGetters({
      configMode: "configStage/configMode",
    }),
  },
  methods: {
    ...mapActions({
      goToNextStep: "configStage/nextConfig",
    }),
  },
};
</script>

<style scoped lang="scss">
.config-toolbar {
  border-top: none;
  min-height: 50px;
  margin: auto !important;

  .btn-group {
    margin-left: auto;
  }
}
</style>
