<template>
  <div class="op-rating">
    <div class="rating-stars">
      <RatingStars :value="model.rating" />
      <span>
        {{ model.username }}, le
        {{ DateTime.fromISO(model.createdAt).toFormat("dd/MM/yyyy") }}
      </span>
    </div>
    <div class="rating-comment" v-if="model.comment">{{ model.comment }}</div>
  </div>
</template>

<script>
import { DateTime } from "luxon";
import RatingStars from "@/components/interface/RatingStars.vue";

/*
 * This component displays a recipe rating+comment
 */
export default {
  name: "Rating",
  props: ["model"],
  data: () => ({
    DateTime,
  }),
  computed: {},
  methods: {},
  components: { RatingStars },
};
</script>

<style lang="scss">
.op-rating {
  display: block;
  padding: 10px;

  .rating-comment {
    margin-top: 5px;
  }
  .rating-stars {
    font-style: italic;
    .op-rating-stars {
      margin-right: 10px;
    }
  }

  .rating-stars,
  .rating-comment {
    padding-left: 10px;
  }
}
</style>
