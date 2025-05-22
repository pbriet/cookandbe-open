<template>
  <select class="form-control form-select" v-model="timeValue" @change="onChange">
    <option v-for="item in items" :value="item.timeValue" :key="item.timeValue">{{ item.label }}</option>
  </select>
</template>

<script>
import { nextDay } from "@/common/dates.js";

/*
 * Displays a combobox with a list of dates between a min and a max
 */
export default {
  name: "DateChoice",
  props: ["modelValue", "minDate", "maxDate"],
  data: () => ({
    items: [],
    timeValue: 0,
  }),
  mounted() {
    this.resetItems();
    this.calcValue();
  },
  computed: {},
  watch: {
    modelValue() {
      this.calcValue();
    },
    minDate() {
      this.resetItems();
    },
    maxDate() {
      this.resetItems();
    },
  },
  methods: {
    onChange() {
      this.$emit("update:modelValue", new Date(this.timeValue));
    },
    /*
     * Value is converted in seconds, because JS date comparison S**CKS !
     */
    calcValue() {
      if (this.modelValue) {
        this.timeValue = this.modelValue.getTime();
      }
    },
    /*
     * Creates the list of choices
     */
    resetItems() {
      if (!this.minDate || !this.maxDate || this.maxDate < this.minDate) {
        this.items = [];
        return;
      }

      const items = [];
      let item = this.minDate;
      while (item <= this.maxDate) {
        const caption = item.getDayName() + " " + item.getDate() + " " + item.getMonthName();
        items.push({ timeValue: item.getTime(), label: caption });
        item = nextDay(item);
      }

      this.items = items;
    },
  },
  components: {},
};
</script>

<style scoped lang="scss"></style>
