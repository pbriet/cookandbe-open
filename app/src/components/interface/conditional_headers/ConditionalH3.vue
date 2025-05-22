<template>
  <ConditionalHeader tag="h3" :when="when">
    <slot></slot>
  </ConditionalHeader>
</template>

<script>
import ConditionalHeader from "@/components/interface/conditional_headers/ConditionalHeader.vue";

export default {
  name: "ConditionalH3",
  props: ["when"],
  computed: {},
  methods: {},
  components: { ConditionalHeader },
};
</script>

<style scoped lang="scss"></style>
