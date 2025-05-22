<template>
  <div class="recipe-viewer-infos">
    <span class="col-12 col-sm-6 info" v-if="recipeData.usage > 0" v-show="canEditRecipe">
      <span class="user-tag">
        <img class="op-icon-md" src="@/assets/img/place/restaurant.png" />
        A été cuisinée {{ recipeData.usage }} fois !
      </span>
    </span>
    <span class="col-12 col-sm-6 info" v-if="recipeData.sourceUrl">
      <span class="user-tag">
        <a :href="recipeData.sourceUrl" target="_blank">
          <span class="op-icon-md">
            <FontAwesomeIcon :icon="['far', 'copyright']" />
          </span>
          {{ extractHostname(recipeData.sourceUrl) }}
        </a>
      </span>
    </span>
    <span class="recipe-infos-times">
      <span class="col-6 info" v-if="recipeData.prepMinutes > 0">
        <span class="user-tag">
          <span class="op-icon-md">
            <FontAwesomeIcon :icon="['far', 'clock']" />
          </span>
          Préparation
          <time itemprop="prepTime" :datetime="`PT${recipeData.prepMinutes}M`">{{ recipeData.prepMinutes }} min </time>.
        </span>
      </span>
      <span class="col-6 info" v-if="recipeData.cookMinutes > 0">
        <span class="user-tag">
          <span class="op-icon-md">
            <FontAwesomeIcon :icon="['far', 'clock']" />
          </span>
          Cuisson
          <time itemprop="cookTime" :datetime="`PT${recipeData.cookMinutes}M`">{{ recipeData.cookMinutes }} min</time>.
        </span>
      </span>
      <span class="col-6 info" v-if="recipeData.restMinutes > 0">
        <span class="user-tag">
          <span class="op-icon-md">
            <FontAwesomeIcon :icon="['far', 'clock']" />
          </span>
          Repos {{ recipeData.restMinutes }} min.
        </span>
      </span>
    </span>

    <div class="clearfix"></div>
  </div>
</template>

<script>
export default {
  name: "Infos",
  props: ["recipeData", "extractHostname", "canEditRecipe"],
  data: () => ({}),
  computed: {},
  methods: {},
  components: {},
};
</script>

<style scoped lang="scss">
.recipe-viewer-infos {
  padding: 15px;

  .info {
    padding-left: 3px;
    padding-right: 3px;
  }

  .tag {
    display: inline-block;
    padding: 2px 5px;
    margin-top: 3px;
    margin-bottom: 3px;
    border-radius: $op-radius-md;
    width: 100%;
  }

  .user-tag {
    @extend .tag;
    background-color: #eeeeee;
  }
}
</style>
