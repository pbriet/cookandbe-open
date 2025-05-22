<template>
  <div class="profile-editor-row">
    <div class="col-12 col-sm-4">{{ caption }}</div>
    <div class="col-12 col-sm-8">
      <select
        class="form-control form-select"
        :value="modelValue"
        @change="onChange"
        :class="{ 'op-invalid-input': mustBeComplete && modelValue === null }"
        :required="mustBeComplete"
      >
        <option v-for="option in options" :value="option.value" :key="option.value">
          {{ option.caption }}
        </option>
      </select>
    </div>
  </div>
</template>

<script>
export default {
  name: "ProfileNapField",
  props: ["modelValue", "options", "caption", "mustBeComplete"],
  methods: {
    onChange(event) {
      this.$emit("update:modelValue", parseInt(event.target.value, 10));
    },
  },
};
</script>

<style scoped lang="scss"></style>
