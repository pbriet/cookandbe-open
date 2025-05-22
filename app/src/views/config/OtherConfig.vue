<template>
  <div class="op-page">
    <div class="op-page-title">
      <h1>Divers</h1>
    </div>
    <ConfigProgression />
    <div class="op-page-content">
      <ConfigBudgetProteins v-model:warning="warning" v-model:values="values" />
    </div>
    <ConfigToolbar />
  </div>
</template>

<script>
import ConfigProgression from "@/components/config/ConfigProgression.vue";
import ConfigBudgetProteins from "@/components/config/ConfigBudgetProteins.vue";
import ConfigToolbar from "@/components/config/ConfigToolbar.vue";

/*
 * View for other configuration page
 */
export default {
  name: "OtherConfig",
  props: [],
  data: () => ({
    warning: {},
    values: {},
  }),
  computed: {},
  methods: {},
  beforeRouteLeave(to, from, next) {
    this.$store.dispatch("configStage/complete", { stageName: "other" });
    next();
  },
  components: { ConfigProgression, ConfigBudgetProteins, ConfigToolbar },
};
</script>

<style scoped lang="scss"></style>
