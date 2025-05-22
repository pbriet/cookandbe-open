<template>
  <div class="op-font-xl op-diet-card">
    <div class="op-diet-img">
      <span class="icon-trophy op-icon-dxxxl" :class="level > 0 ? 'premium-trophy' : 'free-trophy'">
        <FontAwesomeIcon :icon="['fas', 'trophy']" />
      </span>
    </div>
    <div class="op-diet-title">Abonnement {{ SUBSCRIPTION_NAMES[level] }}</div>
  </div>
</template>

<script>
import { SUBSCRIPTION_NAMES } from "@/common/static.js";

export default {
  name: "PremiumTropy",
  props: ["level"],
  data: () => ({
    SUBSCRIPTION_NAMES,
  }),
};
</script>
