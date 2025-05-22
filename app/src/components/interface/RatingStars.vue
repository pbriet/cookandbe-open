<template>
  <span class="op-rating-stars">
    <template v-if="value">
      <FontAwesomeIcon :icon="[valueRounded >= i ? 'fas' : 'far', 'star']" v-for="i in [1, 2, 3, 4, 5]" :key="i" />
      <span class="ratings-values" v-if="withValues">
        (<span :itemprop="microData ? 'ratingValue' : undefined">{{ valueRounded }}</span
        >/<span :itemprop="microData ? 'bestRating' : undefined">5</span>
        <span v-if="nbRatings">
          -
          <span :itemprop="microData ? 'ratingCount' : undefined">{{ nbRatings }}</span>
          vote<span v-if="nbRatings > 1">s</span></span
        >)
      </span>
    </template>
  </span>
</template>

<script>
/*
 * This directive displays 5 stars, filled depending on value
 */
export default {
  name: "RatingStars",
  props: [
    "value",
    "nbRatings",
    "withValues", // Displays (3.5/5) next to the stars. NB: useful for Google Indexing
    "microData",
  ],
  data: () => ({}),
  computed: {
    valueRounded() {
      return Math.round(this.value);
    },
  },
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss">
.op-rating-stars {
  display: inline-block;
  .ratings-values {
    font-size: $op-font-xxs;
  }
}
</style>
