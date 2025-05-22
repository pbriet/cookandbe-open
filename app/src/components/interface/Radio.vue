<template>
  <div
    class="op-checkbox op-radio"
    @click="onToggle"
    :class="{
      'op-checkbox-enabled': !disabled,
      'op-checkbox-disabled': disabled,
      'op-checkbox-focus': caption && !noHover,
    }"
  >
    <span class="op-checkbox-icon op-radio-icon" :class="{ 'op-checkbox-empty': !isChecked }">
      <FontAwesomeIcon :icon="['fas', 'check']" />
    </span>
    <div class="op-checkbox-caption" v-if="caption">{{ caption }}</div>
    <input type="radio" ref="input" :name="group" :value="modelValue" :required="required" style="display: none" />
  </div>
</template>

<script>
/*
 * Pretty radio using Font Awesome
 */
export default {
  name: "Radio",
  props: ["modelValue", "value", "caption", "onChange", "disabled", "required", "noHover", "group"],
  data: () => ({}),
  computed: {
    isChecked() {
      if (this.value.id !== undefined) {
        return this.modelValue && this.modelValue.id === this.value.id;
      } else {
        return this.modelValue === this.value;
      }
    },
  },
  methods: {
    onToggle() {
      if (this.disabled) {
        return;
      }
      this.$emit("update:modelValue", this.value);
      this.onChange && this.onChange(this.value);
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
.op-radio {
  .op-radio-icon {
    border-radius: $op-radius-infinity !important;
  }
}
</style>
