<template>
  <Dialog id="maintenance-modal" class="info in" :open="show">
    <h3 class="dialog-title">Le site est en cours de mise à jour...</h3>

    <div class="dialog-body">
      <h4>Juste un instant SVP !</h4>
      <PleaseWait />
      <span>
        En maintenance
        <span v-if="startedAt"> depuis {{ maintenanceSince }}s</span>
      </span>

      <p>La page sera automatiquement rechargée</p>
    </div>
  </Dialog>
</template>

<script>
import PleaseWait from "@/components/interface/PleaseWait.vue";
import Dialog from "@/components/interface/Dialog.vue";
import { mapGetters } from "vuex";
import API from "@/api.js";

export default {
  name: "MaintenanceModal",
  data: () => ({ startedAt: new Date(), now: new Date() }),
  computed: {
    ...mapGetters({
      show: "dialog/maintenanceModal",
    }),
    maintenanceSince() {
      return Math.round((this.now - this.startedAt) / 1000);
    },
  },
  watch: {
    show(newShow, oldShow) {
      if (!oldShow && newShow) {
        setTimeout(this.checkStatus, 1000);
        this.startedAt = new Date();
        this.now = new Date();
        this.timer = setInterval(() => {
          this.now = new Date();
        }, 1000);
      } else if (oldShow && !newShow) {
        clearInterval(this.timer);
      }
    },
  },
  methods: {
    async checkStatus() {
      try {
        await API.init();
        // Yay, success = maintenance finished
        // Force reload of current page
        window.location.reload(true);
      } catch {
        // Failure : try again
        setTimeout(this.checkStatus, 2000);
      }
    },
  },
  components: { Dialog, PleaseWait },
  beforeUnmount() {
    this.timer && clearInterval(this.timer);
  },
};
</script>
