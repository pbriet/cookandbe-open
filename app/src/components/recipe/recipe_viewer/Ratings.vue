<template>
  <div class="col-12" v-if="recipeRatings.data.length > 0">
    <ConditionalH2 :when="!printMode">
      <span> {{ recipeRatings.data.length }} commentaire<span v-if="recipeRatings.data.length > 1">s</span> : </span>
    </ConditionalH2>

    <SearchPages
      :offset="ratingsPage.offset"
      :count="recipeRatings.nb"
      :resultsPerPage="ratingsPage.nbPerPage"
      :onChangePage="onChangeRatingsPage"
    />

    <div class="op-table">
      <div class="op-row" v-for="rating in recipeRatings.data" :key="rating.id">
        <Rating :model="rating" />
      </div>
    </div>
  </div>
</template>

<script>
import Rating from "@/components/recipe/Rating.vue";
import SearchPages from "@/components/interface/SearchPages.vue";
import ConditionalH2 from "@/components/interface/conditional_headers/ConditionalH2.vue";

export default {
  name: "Ratings",
  props: ["printMode", "recipeRatings", "ratingsPage", "onChangeRatingsPage"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: { Rating, SearchPages, ConditionalH2 },
};
</script>

<style scoped lang="scss"></style>
