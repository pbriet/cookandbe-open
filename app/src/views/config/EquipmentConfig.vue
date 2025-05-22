<template>
  <div class="op-page">
    <div class="op-page-title">
      <h1>Votre équipement</h1>
    </div>
    <ConfigProgression />
    <div class="op-page-content">
      <div id="ustensils-page">
        <EquipmentEditor :userUstensils="user.ustensils" :onToggleUstensil="onToggleUstensil" />
      </div>
    </div>
    <ConfigToolbar />
  </div>
</template>

<script>
import ConfigProgression from "@/components/config/ConfigProgression.vue";
import ConfigToolbar from "@/components/config/ConfigToolbar.vue";
import EquipmentEditor from "@/components/config/EquipmentEditor.vue";
import { mapGetters } from "vuex";

export default {
  name: "EquipmentConfig",
  props: [],
  data: () => ({}),
  computed: {
    ...mapGetters({
      user: "user/get",
    }),
  },
  methods: {
    onToggleUstensil(ustensil, selected) {
      return this.$store.dispatch("user/toggleUstensil", { ustensil, selected });
    },
    save() {
      this.$store.dispatch("configStage/complete", { stageName: "equipment" });
    },
  },
  beforeRouteLeave(to, from, next) {
    this.save();
    next();
  },
  components: { ConfigToolbar, ConfigProgression, EquipmentEditor },
};
</script>

<style scoped lang="scss"></style>
