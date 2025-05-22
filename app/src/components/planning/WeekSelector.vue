<template>
  <div class="op-week-selector">
    <!-- High resolution -->
    <div class="d-none d-md-block">
      <div class="op-tabs-expanded">
        <div class="op-tab icon-cell" @click="gotoPreviousWeek">
          <span class="op-icon-xl">
            <FontAwesomeIcon :icon="['fas', 'backward']" />
          </span>
        </div>
        <div
          class="op-tab week-cell"
          v-for="week in weeks"
          :key="week.key"
          :class="{ active: isCurrentWeek(week) }"
          @click="changeWeek(week)"
        >
          {{ DateTime.fromJSDate(week.firstDay).setLocale("fr").toFormat(shortDateFormat) }}
          au
          {{ DateTime.fromJSDate(week.lastDay).setLocale("fr").toFormat(shortDateFormat) }}
        </div>
        <div class="op-tab icon-cell" @click="gotoNextWeek">
          <span class="op-icon-xl">
            <FontAwesomeIcon :icon="['fas', 'forward']" />
          </span>
        </div>
      </div>
    </div>
    <!-- Low resolution -->
    <div class="d-md-none">
      <div class="op-tabs-expanded">
        <div class="op-tab icon-cell" @click="gotoPreviousWeek">
          <span class="op-icon-xl">
            <FontAwesomeIcon :icon="['fas', 'backward']" />
          </span>
        </div>
        <div class="op-tab week-cell" @click="changeWeek(currentWeek)">
          Du
          {{ DateTime.fromJSDate(currentWeek.firstDay).setLocale("fr").toFormat(longDateFormat) }}
          <br />
          au
          {{ DateTime.fromJSDate(currentWeek.lastDay).setLocale("fr").toFormat(longDateFormat) }}
        </div>
        <div class="op-tab icon-cell" @click="gotoNextWeek">
          <span class="op-icon-xl">
            <FontAwesomeIcon :icon="['fas', 'forward']" />
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { areSameDate, addDays } from "@/common/dates.js";
import { DateTime } from "luxon";

/*
 * This component displays indicators of a day being filled
 */
export default {
  name: "WeekSelector",
  props: {
    baseUrl: {}, // By default, to which url redirecting (baseUrl + '/' + date)
    currentFirstDay: {},
    nbWeeks: {
      default: 3,
    },
  },
  data: () => ({
    weeks: [],
    shortDateFormat: "dd MMM",
    longDateFormat: "dd MMMM",
    DateTime,
  }),
  mounted() {
    this.init(this.currentFirstDay);
  },
  computed: {
    currentWeek() {
      return {
        firstDay: this.currentFirstDay,
        lastDay: addDays(this.currentFirstDay, 6),
      };
    },
  },
  watch: {
    currentFirstDay: {
      handler(newValue) {
        if (newValue) {
          this.init(newValue);
        }
      },
      deep: true,
    },
  },
  methods: {
    init(currentFirstDay) {
      this.weeks = [];
      for (let i = 0; i < this.nbWeeks; ++i) {
        const shift = (i - Math.floor(this.nbWeeks / 2)) * 7;
        const firstDay = addDays(currentFirstDay, shift);
        const lastDay = addDays(currentFirstDay, shift + 6);
        this.weeks.push({ key: i, firstDay, lastDay });
      }
    },
    isCurrentWeek(week) {
      return areSameDate(week.firstDay, this.currentFirstDay);
    },
    gotoPreviousWeek() {
      const firstDay = addDays(this.currentFirstDay, -7);
      this.changeWeek({ firstDay });
    },
    gotoNextWeek() {
      const firstDay = addDays(this.currentFirstDay, +7);
      this.changeWeek({ firstDay });
    },
    changeWeek(week) {
      if (this.isCurrentWeek(week)) {
        return;
      }
      this.$router.push({
        ...this.baseUrl,
        params: { fromDay: week.firstDay.toDateString() },
      });
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
.op-week-selector {
  .week-cell {
    width: 150px;
  }

  .icon-cell {
    width: 60px;
  }
}
</style>
