<template>
  <div
    class="op-font-red fright favorite-infos"
    @mouseenter="mouseover = true"
    @mouseleave="mouseover = false"
    @click="toggleFavorite"
    v-if="!isCustomRecipe && recipeDataId"
  >
    <span class="op-icon-xl" :class="{ 'no-mouse-over': isPersonal }" v-if="isPersonal || inCookbook">
      <FontAwesomeIcon :icon="['fas', 'heart']" />
    </span>
    <span v-if="!isPersonal && !inCookbook">
      <span class="op-icon-xl">
        <FontAwesomeIcon :icon="[mouseover ? 'fas' : 'far', 'heart']" />
      </span>
    </span>
  </div>
</template>

<script>
export default {
  name: "Favorite",
  props: ["toggleFavorite", "recipeDataId", "isCustomRecipe", "isPersonal", "inCookbook"],
  data: () => ({
    mouseover: false,
  }),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss">
.favorite-infos {
  cursor: pointer;

  svg:hover,
  svg[data-prefix="far"] {
    color: lighten($op-color-red, 20%);
  }
  .no-mouse-over:hover svg {
    color: inherit;
    cursor: initial;
  }
  padding-right: 3px;
  padding-top: 5px;
}
</style>
