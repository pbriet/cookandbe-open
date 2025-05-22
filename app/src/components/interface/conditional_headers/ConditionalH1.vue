<template>
  <ConditionalHeader tag="h1" :when="when">
    <slot></slot>
  </ConditionalHeader>
</template>

<script>
import ConditionalHeader from "@/components/interface/conditional_headers/ConditionalHeader.vue";

export default {
  name: "ConditionalH1",
  props: ["when"],
  computed: {},
  methods: {},
  components: { ConditionalHeader },
};
</script>

<style scoped lang="scss"></style>
