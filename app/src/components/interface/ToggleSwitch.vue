<template>
  <div
    class="toggle-switch"
    :class="{
      'toggle-switch--readonly': readonly,
      'toggle-switch--on': modelValue,
      'toggle-switch--off': !modelValue,
    }"
    @click="onToggle"
  >
    <div class="wrapper">
      <span class="toggler-on">Oui</span>
      <span class="spacer">&nbsp;</span>
      <span class="toggler-off">Non</span>
      <input :value="modelValue" type="checkbox" :readonly="readonly" />
    </div>
  </div>
</template>

<script>
export default {
  name: "ToggleSwitch",
  props: ["modelValue", "readonly", "onChange"],
  data: () => ({}),
  computed: {},
  methods: {
    onToggle() {
      if (this.readonly) {
        return;
      }
      this.$emit("update:modelValue", !this.modelValue);
      this.onChange && this.onChange();
    },
  },
};
</script>

<style scoped lang="scss">
.toggle-switch {
  display: inline-block;
  width: 86px;
  cursor: pointer;
  border-radius: 4px;
  border: 1px solid #ccc;
  position: relative;
  overflow: hidden;
  line-height: 8px;
  z-index: 0;
  user-select: none;
  vertical-align: middle;
  .wrapper {
    transition: margin-left 0.5s;
    display: inline-block;
    width: 126px;
    top: 0;
    border-radius: 4px;
  }
}

span {
  width: 42px;
  padding: 5px 9px;
  font-size: 12px;
  line-height: 1.5;
  display: table-cell;
  vertical-align: middle;
  text-align: center;
}

.toggler-on {
  color: white;
  background-color: $op-color-lime;
  border-bottom-left-radius: 3px;
  border-top-left-radius: 3px;
}

.toggler-off {
  color: white;
  background-color: $op-color-alert-danger;
  border-bottom-right-radius: 3px;
  border-top-right-radius: 3px;
}

.spacer {
  margin-top: -1px;
  margin-bottom: -1px;
  background: white;
}

input {
  position: absolute !important;
  top: 0;
  left: 0;
  margin: 0;
  z-index: -1;
  opacity: 0;
  visibility: hidden;
}

.toggle-switch--readonly {
  span {
    opacity: 0.5;
    cursor: default !important;
  }
}
.toggle-switch--off .wrapper {
  margin-left: -42px;
}
.toggle-switch--on .wrapper {
  margin-left: 0;
}
</style>
