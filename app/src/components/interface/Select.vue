<template>
  <div class="btn-group select open" :class="`${selectClasses} ${disabled ? 'disabled' : ''}`">
    <button
      type="button"
      class="btn btn-block d-flex align-items-center dropdown-toggle"
      :class="`${buttonClasses} ${disabled ? 'disabled' : ''}`"
      :disabled="disabled"
      data-bs-toggle="dropdown"
      role="button"
      aria-expanded="false"
    >
      <span class="current-option">
        <slot name="option" :option="currentOption">
          {{ option.label }}
        </slot>
      </span>
    </button>
    <ul class="dropdown-menu">
      <li class="dropdown-item" v-for="option in options" :key="option.value" @click="onClick(option.value)">
        <slot name="option" :option="option">
          {{ option.label }}
        </slot>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "Select",
  props: ["disabled", "options", "modelValue", "selectClasses", "buttonClasses"],
  data: () => ({}),
  computed: {
    currentOption() {
      return this.options.filter((option) => option.value == this.modelValue)[0];
    },
  },
  methods: {
    onClick(value) {
      if (!this.disabled) {
        this.$emit("update:modelValue", value);
      }
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
.select {
  display: inline-block;
  padding: 0;
}

.select.disabled {
  cursor: not-allowed;
}

.dropdown-toggle,
.dropdown-menu,
.dropdown-item {
  width: 100%;
}

.dropdown-item:hover {
  cursor: pointer;
}

.current-option {
  margin-right: auto;
}
</style>
