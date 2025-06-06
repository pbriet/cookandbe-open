<template>
  <input
    type="text"
    ref="input"
    :min="min"
    :max="max"
    :required="required"
    v-on:input="validate($event.target.value)"
    :class="{ 'op-invalid-input': required && !value, 'form-control': formControl }"
    :placeholder="placeholder"
  />
</template>

<script>
/*
 * Input with a float.
 *
 * Accepts both commas and dots.
 * Checks that the value is between min and max
 * Display it in red if value is incorrect or unset
 * http://wemadeyoulook.at/en/blog/comma-dot-input-typenumber-mess/
 */
const FLOAT_REGEXP = /^-?\d+((\.|,)\d+)?$/;

export default {
  name: "SmartFloatInput",
  props: {
    modelValue: {},
    min: {},
    max: {},
    placeholder: {},
    required: {},
    formControl: {
      default: true,
    },
  },
  data: function () {
    return {
      value: this.modelValue,
    };
  },
  mounted() {
    this.$refs.input.value = this.modelValue ?? "";
  },
  watch: {
    modelValue(newModelValue) {
      if (newModelValue != this.value) {
        this.$refs.input.value = newModelValue ?? "";
        this.validate(this.$refs.input.value, false);
      }
    },
  },
  methods: {
    validate(rawValue, emitEvent = true) {
      let value = null;
      if (FLOAT_REGEXP.test(rawValue)) {
        if (typeof rawValue === "number") {
          value = rawValue;
        } else {
          value = parseFloat(rawValue.replace(",", "."));
        }
        if ((this.min && value < this.min) || (this.max && value > this.max)) {
          value = null;
        }
      }
      this.value = value;
      if (emitEvent) {
        this.$emit("update:modelValue", this.value);
      }
    },
  },
};
</script>
