<template>
  <div id="op-day-view-page" class="op-page">
    <div class="op-page-title">
      <h1>Mes repas</h1>
    </div>

    <div id="day-view-content">
      <DaySelector baseUrl="DayView" baseUrlFuture="DayPlanner" baseUrlToday="DayPlanner" :currentDate="date" />

      <!-- Selection menu -->
      <div id="day-view-left-menu" class="op-column">
        <div class="day-view-menu-title">
          {{ upperFirst(DateTime.fromJSDate(date).setLocale("fr").toFormat("EEEE dd MMMM")) }}
        </div>

        <div v-if="day && day.filled && !day.future">
          <div v-for="mealType in mealTypes" :key="mealType.id" v-show="isMealVisible(day, mealType)">
            <div class="day-view-menu-meal-title">{{ mealType.name }}</div>

            <div v-if="day.mealSlots[mealType.id].external" class="day-view-menu-item">A l'extérieur</div>
            <template v-if="!day.mealSlots[mealType.id].external">
              <div v-for="dish in day.mealSlots[mealType.id].dishes" :key="dish.id">
                <div
                  @click="moveTo(dish, recipe)"
                  v-for="recipe in dish.recipes"
                  :key="recipe.id"
                  class="day-view-menu-item day-view-menu-link"
                >
                  {{ recipe.name }}
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
      <!-- Selection menu -->

      <!-- Detailed recipes -->
      <div id="day-view-recipe-list" class="op-column" v-if="day">
        <div class="col-md-12" v-if="day.future || !day.filled">
          <br />

          <div class="alert alert-danger op-font-xl" v-if="day.future">
            <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" /> (futur)
          </div>
          <div class="alert alert-warning op-font-xl d-flex" v-if="!day.filled">
            <span class="op-hs-5 op-icon-dxl">
              <FontAwesomeIcon :icon="['fas', 'info-circle']" />
            </span>
            <p class="d-inline-block ms-1">
              Aucun repas planifié pour cette journée.<br />
              La modification de repas passés n'est pas encore disponible !
            </p>
          </div>
        </div>

        <div v-if="day.filled && !day.future">
          <div v-for="mealType in mealTypes" :key="mealType.id" v-show="isMealVisible(day, mealType)">
            <div class="day-view-meal-title">{{ mealType.name }}</div>

            <!-- External dishes -->
            <div class="day-view-recipe recipe-external" v-if="!isCooked(day, mealType)">
              <img class="op-icon-dxxl" :src="placeImg(PLACES[day.mealSlots[mealType.id].placeKey].img)" />
              <div>A l'extérieur</div>
            </div>

            <!-- Cooked dishes -->
            <template v-if="isCooked(day, mealType)">
              <div v-for="dish in day.mealSlots[mealType.id].dishes" :key="dish.id">
                <div
                  class="day-view-recipe"
                  :class="`day-view-dish-${dish.id}-recipe-${recipe.id}`"
                  v-for="recipe in dish.recipes"
                  :key="recipe.id"
                >
                  <RecipeViewer :recipeId="recipe.id" :ratio="recipe.ratio" :showDetails="true" />
                  <RecipeViewer :recipeId="recipe.id" :ratio="recipe.ratio" :showDetails="true" :printMode="true" />
                </div>
              </div>
            </template>
            <!-- dish -->
          </div>
          <!-- meal_type -->
        </div>
        <!-- if filled -->
      </div>
      <!-- day-view-recipe-list -->
    </div>
    <!-- day-view-content -->
  </div>
  <!-- op-day-view-page -->
</template>

<script>
import { PLACES } from "@/common/static.js";
import DaySelector from "@/components/planning/DaySelector.vue";
import RecipeViewer from "@/components/recipe/recipe_viewer/RecipeViewer.vue";
import { mapGetters, mapMutations } from "vuex";
import { DateTime } from "luxon";
import { upperFirst } from "lodash";
import { stringToDate } from "@/common/dates.js";
import API from "@/api.js";
import $ from "jquery";

/*
 * View for displaying recipes in a day
 */
export default {
  name: "DayView",
  props: [],
  data() {
    return {
      PLACES,
      day: null,
      mealTypes: [],
      DateTime,
    };
  },
  mounted() {
    this.init(this.date);
    window.addEventListener("scroll", this.updateMenuCss);
  },
  beforeUnmount() {
    window.removeEventListener("scroll", this.updateMenuCss);
  },
  computed: {
    ...mapGetters({
      user: "user/get",
    }),
    date() {
      return stringToDate(this.$route.params.day);
    },
  },
  methods: {
    upperFirst,
    ...mapMutations({
      metaSetTitle: "meta/setTitle",
    }),
    init(date) {
      this.metaSetTitle(upperFirst(DateTime.fromJSDate(date).setLocale("fr").toFormat("EEEE dd MMMM")));
      // TODO: optimize - this is done quickly
      API.userDays.get(this.user.id, date.toDateString(), { allow_empty_days: true, nb_days: 1 }).then((data) => {
        this.day = data["content"]["days"][0];
        this.mealTypes = data["content"]["mealTypes"];
      });
    },
    // Scroll to recipe
    moveTo(dish, recipe) {
      const target = $(`.day-view-dish-${dish.id}-recipe-${recipe.id}`);
      $("body,html").animate({ scrollTop: target.offset().top }, "slow");
    },
    updateMenuCss() {
      // Correspond à la variable less $op-page-padding-top-sm + menu-top-height + day-selector-heigh
      const opPagePaddingTop = 75 + 75 + 60;
      // Retrait par rapport au haut de la fenêtre
      const marginTop = 20;
      // Total
      const scrollThreshold = opPagePaddingTop - marginTop;

      const $el = $("#day-view-left-menu");
      const $window = $(window);
      if ($window.scrollTop() > scrollThreshold && $el.css("position") != "fixed") {
        $el.css({ position: "fixed", top: marginTop + "px" });
      }
      if ($window.scrollTop() < scrollThreshold && $el.css("position") == "fixed") {
        $el.css({ position: "relative", top: "0px" });
      }
    },
    isMealVisible(day, mealType) {
      const meal = this.$route.params.meal;
      return day.mealSlots[mealType.id] && (!meal || meal == mealType.name);
    },
    isCooked(day, mealType) {
      const key = day.mealSlots[mealType.id].placeKey;
      return key == "home" || key == "lunchpack";
    },
    placeImg(place) {
      return require(`@/assets/img/${place}`);
    },
  },
  beforeRouteUpdate(to, _, next) {
    // Called when $route.params.day changes
    this.init(stringToDate(to.params.day));
    next();
  },
  components: { DaySelector, RecipeViewer },
};
</script>

<style scoped lang="scss">
#op-day-view-page {
  $day-view-content-width-md: ($op-page-column-width-xs + $op-page-column-width-md);
  $day-view-content-width-sm: ($op-page-column-width-md + 2 * $op-page-content-border-width);

  #day-view-content {
    margin: auto;
    width: 100%;

    &:after {
      @extend .clearfix;
    }
  }

  #day-view-left-menu {
    float: left;
    height: inherit;
    min-height: 0px;
    position: relative;
    margin-top: -1px;
    border-right: none;
    width: 0px;
    display: none;

    .day-view-menu-title {
      text-align: center;
      width: 100%;
      font-size: $op-font-xxl;
      color: $op-color-green;
      padding: 10px;
    }

    .day-view-menu-meal-title {
      text-align: center;
      font-size: $op-font-xl;
      margin: 5px;
      padding-top: 15px;
      border-bottom: $op-page-content-border-width solid $op-color-border;
    }

    .day-view-menu-item {
      text-align: center;
      padding: 2px;
    }
    .day-view-menu-link {
      &:hover {
        cursor: pointer;
        color: $op-color-red;
      }
    }
  }

  #day-view-recipe-list {
    float: right;
    padding: 0px;
    border-top: none;
    width: 100%;

    .day-view-meal-title {
      text-align: center;
      font-size: $op-font-xxxl;
      padding-top: 50px;
      padding-bottom: 10px;
      margin: 0px 20px;
    }

    .day-view-recipe {
      border-top: $op-page-content-border-width solid $op-color-border;
      margin: 0px 20px;
      padding: 10px 0px;
    }

    .recipe-external {
      text-align: center;
      font-size: $op-font-lg;
    }
  }
}
</style>
