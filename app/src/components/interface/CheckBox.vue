<template>
  <div
    class="op-checkbox"
    @click="onToggle"
    :class="{
      'op-checkbox-enabled': !disabled,
      'op-checkbox-disabled': disabled,
      'op-checkbox-focus': caption !== undefined,
    }"
  >
    <div>
      <span class="op-checkbox-icon" :class="{ 'op-checkbox-empty': !isChecked }">
        <FontAwesomeIcon :icon="['fas', iconOrDefault]" />
      </span>
    </div>
    <div class="op-checkbox-caption" v-if="caption">{{ caption }}</div>
  </div>
</template>

<script>
/*
 * Pretty checkbox using Font Awesome
 */
export default {
  name: "Checkbox",
  props: ["caption", "onChange", "modelValue", "disabled", "icon", "checked"],
  data: () => ({}),
  computed: {
    isChecked() {
      if (this.modelValue !== undefined) {
        return this.modelValue;
      }
      return this.checked;
    },
    iconOrDefault() {
      return this.icon || "check";
    },
  },
  methods: {
    onToggle() {
      if (this.disabled) {
        return;
      }

      if (this.modelValue !== undefined) {
        this.$emit("update:modelValue", !this.isChecked);
      }
      this.onChange && this.onChange(!this.isChecked);
    },
  },
};
</script>

<style lang="scss">
.op-checkbox {
  width: 100%;
  display: flex;
  align-items: center;
  margin-right: 4px;

  .op-checkbox-icon {
    display: flex;
    align-items: center;

    font-size: 70%;
    padding: 2px;
    border-radius: $op-radius-sm;
    margin-right: 4px;
    margin-bottom: 2px;
    margin-left: 5px;
    background-color: white;
  }

  .op-checkbox-caption {
    width: 100%;
  }

  .op-checkbox-empty svg {
    color: transparent !important;
  }
}

.op-checkbox.op-checkbox-disabled {
  .op-checkbox-icon {
    border: 1px solid $op-color-text-soft;
    color: $op-color-text-soft;
  }

  .op-checkbox-caption {
    color: $op-color-text-soft;
  }

  &:hover {
    cursor: default;
  }
}

.op-checkbox.op-checkbox-enabled {
  .op-checkbox-icon {
    border: 1px solid $op-color-text-main;
  }

  &:hover {
    cursor: pointer;
  }
}

.op-checkbox.op-checkbox-enabled.op-checkbox-focus {
  &:hover {
    color: black;
    background-color: $op-color-grey-light;

    .op-checkbox-icon {
      border: 1px solid black;
    }
  }
}
</style>
