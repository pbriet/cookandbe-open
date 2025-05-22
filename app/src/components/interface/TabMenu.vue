<template>
  <div class="text-center">
    <div class="op-tabs-expanded op-tab-submenu">
      <span
        v-for="elt in elements"
        class="op-tab"
        :class="{ active: elt.key == selectedTab }"
        :key="elt.key"
        @click="onClick(elt)"
      >
        {{ elt.caption }}
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: "TabMenu",
  props: ["elements", "selectedTab", "onTabClick"],
  data: () => ({}),
  computed: {},
  methods: {
    onClick(clickedElt) {
      this.onTabClick(clickedElt.key);
    },
  },
  components: {},
};
</script>

<style scoped lang="scss"></style>
