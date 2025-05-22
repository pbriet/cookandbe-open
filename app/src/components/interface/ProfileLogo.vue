<template>
  <div class="profile-icon" :style="style">
    <span :class="{ male: sex == 'male' && !noColor, female: sex == 'female' && !noColor }">
      <FontAwesomeIcon :icon="['fas', 'user']" />
    </span>
  </div>
</template>

<script>
/*
 * This component displays a logo given a profile
 */
export default {
  name: "ProfileLogo",
  props: ["sex", "noColor", "style"],
};
</script>

<style scoped lang="scss">
.profile-icon {
  font-size: $op-font-dxxl;
  line-height: $op-font-dxxl;
  .female {
    color: $op-color-female;
  }
  .male {
    color: $op-color-male;
  }
}
</style>
