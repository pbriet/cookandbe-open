<template>
  <div id="op-calendar-page" class="op-page">
    <div class="d-print-none">
      <div class="op-page-title">
        <h1>
          Mes repas
          <a class="fright op-font-dxl d-none d-sm-inline" @click="onPrint">
            <FontAwesomeIcon :icon="['fas', 'print']" />
          </a>
        </h1>
      </div>

      <div>
        <WeekSelector v-if="firstDay" :baseUrl="{ name: 'Calendar' }" :currentFirstDay="firstDay" />
        <div class="op-page-content">
          <div class="d-none d-sm-block">
            <CalendarLg
              v-if="planning"
              v-model:selection="selection"
              :planning="planning"
              :dateFormat="dateFormat"
              :clickDay="clickDay"
            />
          </div>
          <div class="calendar-xs d-sm-none">
            <CalendarXs
              v-if="planning"
              v-model:selection="selection"
              :planning="planning"
              :dateFormat="dateFormat"
              :clickDay="clickDay"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Version imprimable -->
    <div class="d-none d-print-block">
      <CalendarPrint v-if="planning" :planning="planning" :dateFormat="dateFormat" />
    </div>
  </div>
</template>

<script>
import { mapGetters, mapMutations } from "vuex";
import { PLACES } from "@/common/static.js";
import {
  stringToDate,
  addDays,
  todayAtMidnight,
  nextMonday,
  previousMonday,
  weekEndFromWeekStart,
  isFuture,
  isToday,
  isPast,
} from "@/common/dates.js";
import { DateTime } from "luxon";
import { randInt } from "@/common/numbers.js";
import { differenceBy } from "lodash";
import API from "@/api.js";
import CalendarPrint from "@/views/planning/CalendarPrint.vue";
import CalendarXs from "@/views/planning/CalendarXs.vue";
import CalendarLg from "@/views/planning/CalendarLg.vue";
import WeekSelector from "@/components/planning/WeekSelector.vue";

/*
 * View for displaying a week, from Monday to Sunday, with no interaction
 */
export default {
  name: "Calendar",
  props: [],
  mounted() {
    this.init(this.$route.params.fromDay);
  },
  data: () => ({
    planning: null,
    selection: { activeDay: null },
    firstDay: null,
    lastDay: null,
    showPleaseWait: false,
    dateFormat: "EEEE dd",
  }),
  computed: {
    ...mapGetters({
      user: "user/get",
    }),
  },
  methods: {
    ...mapMutations({
      metaSetTitle: "meta/setTitle",
    }),
    init(fromDay) {
      if (fromDay) {
        this.firstDay = stringToDate(fromDay);
        if (this.firstDay.getDay() != 1) {
          this.firstDay = addDays(this.firstDay, 1 - this.firstDay.getDay());
        }
      } else {
        if (todayAtMidnight().getDay() === 0) {
          // We are sunday, display next week
          this.firstDay = nextMonday();
        } else {
          // We are monday-saturday, display current week
          this.firstDay = previousMonday();
        }
      }
      this.lastDay = weekEndFromWeekStart(this.firstDay);
      this.metaSetTitle(
        `Semaine du ${DateTime.fromJSDate(this.firstDay).toFormat("dd/MM")} au ${DateTime.fromJSDate(
          this.lastDay
        ).toFormat("dd/MM")}`
      );
      // Loading planning
      this.reloadPlanningCallback();
      this.initDaySelection();
    },
    onPrint() {
      window.print();
    },
    initDaySelection() {
      this.selection = { activeDay: null };
    },
    /*
     * Reload the user default planning
     */
    async reloadPlanningCallback() {
      const data = await API.userDays.get(this.user.id, this.firstDay.toDateString(), { allow_empty_days: true });
      this.endPleaseWait();
      // Ugly : when planning is totally empty, there is no row
      if (data.content.mealTypes.length === 0) {
        data.content.mealTypes = ["something"];
      }
      this.planning = data.content;
      for (const day of this.planning.days) {
        this.initDay(data.content, day);
      }
      this.selectFocusedRecipes(this.planning);
    },
    pleaseWait() {
      this.showPleaseWait = true;
    },
    endPleaseWait() {
      this.showPleaseWait = false;
    },
    initDay(planning, day) {
      day.recipePhotoList = [];
      day.date = stringToDate(day.date);
      day.isFuture = isFuture(day.date);
      day.isToday = isToday(day.date);
      day.isPast = isPast(day.date);
      day.isFutureOrToday = day.isFuture || day.isToday;
      day.clickable = this.isClickable(day);
      for (const mealType of planning.mealTypes) {
        let mealSlot = day.mealSlots[mealType.id];

        if (!mealSlot) {
          mealSlot = day.mealSlots[mealType.id] = { empty: true, placeKey: "donoteat" };
        }
        if (!day.filled || mealSlot.cooked) {
          mealSlot.place = null;
          this.searchRecipePhotos(day, mealSlot);
          continue;
        }
        mealSlot.place = PLACES[mealSlot.placeKey];
      }
    },
    isClickable(day) {
      if (day.isFutureOrToday) {
        return true; // Future days lead to day planner, all right
      }
      if (!day.filled) {
        return false; // This day wasn't planned
      }
      return true;
    },
    searchRecipePhotos(day, mealSlot) {
      if (mealSlot.dishes) {
        for (let j = 0; j < mealSlot.dishes.length && !day.focusedRecipe; ++j) {
          const dish = mealSlot.dishes[j];
          for (let k = 0; k < dish.recipes.length && !day.focusedRecipe; ++k) {
            const recipe = dish.recipes[k];
            if (recipe.photo && day.filled) {
              day.recipePhotoList.push(recipe);
            }
          }
        }
      }
    },
    selectFocusedRecipes(planning) {
      // Creates a copy
      const days = [...planning.days];
      // Inplace sort according to the number of recipe's photos available
      days.sort((d1, d2) => d1.recipePhotoList.length - d2.recipePhotoList.length);
      // Selecting photos to avoid duplication
      const usedPhotos = [];
      for (const day of days) {
        day.focusedRecipe = { photo: null };

        if (day.recipePhotoList.length > 0) {
          let candidatePhoto = day.recipePhotoList[0];

          day.recipePhotoList = differenceBy(day.recipePhotoList, usedPhotos, (recipe) => recipe.id);
          if (day.recipePhotoList.length !== 0) {
            candidatePhoto = day.recipePhotoList[randInt(day.recipePhotoList.length - 1)];
          }
          usedPhotos.push(candidatePhoto);
          day.focusedRecipe = candidatePhoto;
        }
      }
    },
    clickDay(day) {
      // Empty in the past : nothing you can do!
      if (!day.clickable) {
        return;
      }
      if (day.isFuture || day.isToday) {
        this.fillDay(day);
        return;
      }
      this.$router.push({ name: "DayView", params: { day: day.date.toDateString() } });
    },
    fillDay(day) {
      // Redirecting to day review
      this.$router.push({ name: "DayPlanner", params: { day: day.date.toDateString() } });
    },
  },
  beforeRouteUpdate(to, _, next) {
    // Called when $route.params.fromDay changes
    this.init(to.params.fromDay);
    next();
  },
  components: { CalendarPrint, CalendarXs, CalendarLg, WeekSelector },
};
</script>

<style lang="scss">
$default-calendar-heigh: 480px;

#op-calendar-page {
  $today_bg_color: #e9e9e9;

  .alert {
    text-align: center;
    font-size: $op-font-lg;

    .glyphicon {
      vertical-align: middle;
    }
  }

  .op-page-content {
    padding: 0px;
    padding-top: 1px;
    border-top: none;
  }

  .calendar {
    margin-top: 10px;
    min-height: $default-calendar-heigh;
    height: $default-calendar-heigh;
    width: 100%;
    border-collapse: collapse;

    .calendar-day-title {
      font-size: $op-font-lg;
      vertical-align: bottom;
      height: 80px;
      text-align: center;

      @media print {
        height: inherit;
      }
    }

    td,
    th {
      width: 14%;
      border-left: 5px solid white;
      border-right: 5px solid white;
      border-bottom: 3px solid white;
      border-top: 3px solid white;

      @media print {
        border: 1px solid black !important;
      }
    }

    .past_day {
      background-color: $op-color-grey-light;
    }
    .present_day {
      background-color: $today_bg_color;
    }
    .future_day {
      background-color: $op-color-grey-light;
    }
  }

  .dish {
  }

  .dish_recipe {
    margin-bottom: 4px;
    font-size: $op-font-sm;
    padding: 3px;
    line-height: 120%;
  }

  .meal_slot {
    text-align: center;
    padding-top: 10px;
    padding-bottom: 5px;
    font-size: $op-font-md;
    font-weight: normal;
  }

  .past_day {
    color: $op-color-text-soft;
  }

  .present_day {
    color: black;
  }

  .future_day {
    color: $op-color-text-main;
  }

  .clickable_meal_slot:hover {
    cursor: pointer;
  }

  .clickable_meal_slot.selected_meal_slot {
    background-color: $op-color-green-light !important;
  }

  @media print {
    @page {
      size: landscape;
    }
  }
}
</style>
