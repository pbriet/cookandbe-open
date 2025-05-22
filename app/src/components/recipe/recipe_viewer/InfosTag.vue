<template>
  <div class="recipe-info-tags row row-cols-auto row-cols-sm-1 row-cols-lg-2">
    <div class="col-sm info-tag">
      <div class="main-info">
        <span v-for="option in recipePriceOptions" :key="option.id">
          <img src="@/assets/img/recipe/cost.png" class="me-1" />
        </span>
      </div>
      <div class="separator"></div>
      <div class="secondary-info">
        <div>{{ recipePriceOption.label }}</div>
      </div>
    </div>

    <div class="col-sm info-tag">
      <div class="main-info">
        <span v-for="option in recipeDifficultyOptions" :key="option.id">
          <img src="@/assets/img/recipe/toque.png" class="me-1" />
        </span>
      </div>
      <div class="separator"></div>
      <div class="secondary-info">
        <div>{{ recipeDifficultyOption.label }}</div>
      </div>
    </div>

    <div class="col-sm info-tag" v-if="recipeData.nbRatings > 0">
      <div class="main-info op-font-xxl">
        <RatingStars :value="recipeData.avgRating" />
        {{ recipeAvgRating }}
      </div>
      <div class="separator"></div>
      <div class="secondary-info">
        <span class="d-sm-none">(</span>{{ recipeData.nbRatings }} avis<span class="d-sm-none">)</span>
      </div>
    </div>

    <div class="col-sm info-tag" v-if="recipeData.usage > 0" v-show="canEditRecipe">
      <div class="main-info op-font-xxl">
        <FontAwesomeIcon :icon="['fas', 'utensils']" />
        {{ recipeData.usage }}
      </div>
      <div class="separator"></div>
      <div class="secondary-info">personnes l'ont testé</div>
    </div>

    <div class="col-sm info-tag">
      <div class="main-info">
        <FontAwesomeIcon :icon="['far', 'clock']" v-if="recipeData.speed" />
        <span class="ms-1">
          {{ recipeSpeedOption.label }}
        </span>
      </div>
      <div class="separator"></div>
      <span class="d-sm-none secondary-info">
        (
        <span>
          Prép.
          <time itemprop="prepTime" :datetime="`PT${recipeData.prepMinutes}M`">{{ recipeData.prepMinutes }} min</time>
        </span>
        /
        <span>
          Cui.
          <time itemprop="cookTime" :datetime="`PT${recipeData.cookMinutes}M`">{{ recipeData.cookMinutes }} min</time>
        </span>
        /
        <span>
          Rep.
          <time>{{ recipeData.restMinutes }} min</time>
        </span>
        )
      </span>
      <div class="d-none d-sm-block secondary-info">
        <div>
          Préparation
          <time itemprop="prepTime" :datetime="`PT${recipeData.prepMinutes}M`">{{ recipeData.prepMinutes }} min</time>
        </div>
        <div>
          Cuisson
          <time itemprop="cookTime" :datetime="`PT${recipeData.cookMinutes}M`">{{ recipeData.cookMinutes }} min</time>
        </div>
        <div>
          Repos
          <time>{{ recipeData.restMinutes }} min</time>
        </div>
      </div>
    </div>

    <div class="col-12 col-sm col-lg-6 info-tag">
      <router-link
        :to="{ name: 'RecipeView', params: { recipeKey: recipeData.urlKey }, query: { ratio, autoprint: true } }"
        rel="nofollow"
        target="_blank"
        class="recipe-viewer-print-btn text-center"
        v-if="displayPrint"
      >
        <span class="op-icon-xl">
          <FontAwesomeIcon :icon="['fas', 'print']" />
        </span>
        Imprimer
      </router-link>
    </div>

    <div class="col-sm-12 col-lg-12 info-tag" v-if="recipeData.sourceUrl && !recipeData.blog">
      <div class="main-info main-info-source-url">
        <FontAwesomeIcon :icon="['far', 'copyright']" />
        <a :href="recipeData.sourceUrl" target="_blank" class="ms-1">
          {{ extractHostname(recipeData.sourceUrl) }}
        </a>
      </div>
    </div>

    <span class="clearfix" />
  </div>
</template>

<script>
import { RECIPE_PRICE_OPTIONS, RECIPE_DIFFICULTY_OPTIONS, RECIPE_SPEED_OPTIONS } from "@/common/static.js";
import RatingStars from "@/components/interface/RatingStars.vue";

export default {
  name: "InfosTag",
  props: ["recipeData", "canEditRecipe", "extractHostname", "displayPrint", "ratio", "fullUrl"],
  data: () => ({}),
  computed: {
    recipePriceOptions() {
      return RECIPE_PRICE_OPTIONS.filter((_, index) => index < this.recipeData.price);
    },
    recipePriceOption() {
      return RECIPE_PRICE_OPTIONS.filter((option) => option.id === this.recipeData.price)[0];
    },
    recipeDifficultyOptions() {
      return RECIPE_DIFFICULTY_OPTIONS.filter((_, index) => index < this.recipeData.difficulty);
    },
    recipeDifficultyOption() {
      return RECIPE_DIFFICULTY_OPTIONS.filter((option) => option.id === this.recipeData.difficulty)[0];
    },
    recipeSpeedOption() {
      return RECIPE_SPEED_OPTIONS.filter((option) => option.id === this.recipeData.speed)[0];
    },
    recipeAvgRating() {
      return new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(
        this.recipeData.avgRating
      );
    },
  },
  methods: {},
  components: { RatingStars },
};
</script>

<style scoped lang="scss">
.recipe-info-tags {
  @media (max-width: $bootstrap-xs-max) {
    padding: 10px;
  }
}

.recipe-viewer-print-btn {
  &:hover {
    color: $op-color-lime;
    cursor: pointer;
  }
  padding-top: 10px;
  display: block;
  color: $op-color-text-main;
}

.main-info-source-url {
  text-align: left;
}

.info-tag {
  @media (max-width: $bootstrap-xs-max) {
    display: inline;
    white-space: nowrap;
    padding: 0px 5px;

    div {
      display: inline;
    }

    .main-info {
      @include op-font-md;
      img {
        width: 15px;
      }
    }
    .secondary-info {
      @include op-font-md;
    }
    .separator {
      display: none;
    }
  }

  @media (min-width: $bootstrap-sm-min) {
    text-align: center;
    padding: 10px 5px;

    .main-info {
      @include op-font-xl;
      img {
        width: 20px;
      }
    }
    .secondary-info {
      @include op-font-md;
    }
    .separator {
      width: 75%;
      height: 1px;
      border-top: 1px solid #cccccc;
      margin: auto;
      margin-top: 5px;
      margin-bottom: 5px;
    }
  }
}
</style>
