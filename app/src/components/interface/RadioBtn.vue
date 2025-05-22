<template>
  <button
    class="btn radio-btn"
    :class="{ 'btn-info': modelValue === value, 'btn-secondary': modelValue !== value }"
    @click="selectValue"
  >
    <slot></slot>
  </button>
</template>

<script>
/*
 * Like a radio, but with multiple buttons, one being selected.
 */
export default {
  name: "RadioBtn",
  props: ["modelValue", "value", "caption", "onClick"],
  data: () => ({}),
  computed: {},
  methods: {
    selectValue() {
      this.$emit("update:modelValue", this.value);
      this.onClick && this.onClick(this.value);
    },
  },
  components: {},
};
</script>

<style scoped lang="scss"></style>
