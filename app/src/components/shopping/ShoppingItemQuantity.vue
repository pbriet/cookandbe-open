<template>
  <span v-if="item.forcedQuantity"> {{ item.forcedQuantity }} </span>
  <span v-if="!item.forcedQuantity">
    <span v-html="conversionClean(item.conversion, item.food.name)" class="d-table-cell"></span>
    <span class="gram-equivalent" v-if="item.basicConversion">
      (<span v-html="item.basicConversion.htmlValue"></span> {{ item.basicConversion.unit }})
    </span>
  </span>
</template>

<script>
import { conversionClean } from "@/common/filters.js";

export default {
  name: "ShoppingItemQuantity",
  props: ["item"],
  data: () => ({}),
  computed: {},
  methods: {
    conversionClean,
  },
  components: {},
};
</script>

<style scoped lang="scss"></style>
