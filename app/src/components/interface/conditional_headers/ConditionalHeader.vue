<template>
  <span class="conditional" :class="`conditional-${tag}`">
    <component :is="tag" v-if="when"><slot></slot></component>
    <slot v-else></slot>
  </span>
</template>

<script>
export default {
  name: "ConditionalHeader",
  props: ["when", "tag"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss"></style>
