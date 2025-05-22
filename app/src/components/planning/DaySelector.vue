<template>
  <div class="op-day-selector">
    <!-- High resolution -->
    <div class="d-none d-md-block">
      <div class="op-tabs-expanded" v-if="dateStates">
        <router-link class="op-tab icon-cell" :to="{ name: 'Calendar' }">
          <FontAwesomeIcon :icon="['fas', 'calendar-alt']" />
        </router-link>
        <div
          class="op-tab day-cell"
          v-for="(date, index) in dates"
          :key="date"
          :class="{
            active: isCurrentDate(date),
            to_be_created: dateStates.states[index] === 'empty' && !isCurrentDate(date),
          }"
          @click="changeDate(date)"
        >
          <FontAwesomeIcon
            :icon="['fas', 'plus']"
            v-if="dateStates.states[index] === 'empty' && !isCurrentDate(date)"
          />
          {{ upperFirst(DateTime.fromJSDate(date).setLocale("fr").toFormat("EEEE dd")) }}
        </div>
      </div>
    </div>
    <!-- Low resolution -->
    <div class="d-md-none">
      <div class="op-tabs-expanded">
        <router-link class="op-tab icon-cell" :to="{ name: 'Calendar' }">
          <FontAwesomeIcon :icon="['fas', 'calendar-alt']" />
        </router-link>
        <div class="op-tab icon-cell" @click="gotoYesterday" :class="{ to_be_created: isYesterdayEmpty }">
          <FontAwesomeIcon :icon="['fas', 'plus']" v-if="isYesterdayEmpty" />
          <FontAwesomeIcon :icon="['fas', 'chevron-left']" />
        </div>
        <div class="op-tab day-cell active">
          {{ upperFirst(DateTime.fromJSDate(currentDate).setLocale("fr").toFormat("EEEE dd")) }}
        </div>
        <div class="op-tab icon-cell" @click="gotoTomorrow" :class="{ to_be_created: isTomorrowEmpty }">
          <FontAwesomeIcon :icon="['fas', 'plus']" v-if="isTomorrowEmpty" />
          <FontAwesomeIcon :icon="['fas', 'chevron-right']" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import API from "@/api.js";
import { addDays, areSameDate, isToday, isPast, isFuture } from "@/common/dates.js";
import { DateTime } from "luxon";
import { upperFirst } from "lodash";

/*
 * This component displays indicators of a day being filled
 */
export default {
  name: "DaySelector",
  props: {
    baseUrl: {}, // By default, to which url redirecting (baseUrl + '/' + date)
    baseUrlPast: {}, // Overrides default for past
    baseUrlFuture: {}, // Overrides default for future
    baseUrlToday: {}, // Overrides default for today
    currentDate: {},
    nbDays: {
      default: 5,
    },
  },
  data: () => ({
    dates: [],
    dateStrs: [],
    dateStates: null,
    DateTime,
  }),
  mounted() {
    this.init(this.currentDate);
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
    }),
    isYesterdayEmpty() {
      if (!this.dateStates || !this.dateStates.states) {
        return false;
      }
      const yesterday = addDays(this.currentDate, -1).toDateString();
      const iDate = this.dateStrs.indexOf(yesterday);
      return this.dateStates.states[iDate] === "empty";
    },
    isTomorrowEmpty() {
      if (!this.dateStates || !this.dateStates.states) {
        return false;
      }
      const tomorrow = addDays(this.currentDate, 1).toDateString();
      const iDate = this.dateStrs.indexOf(tomorrow);
      return this.dateStates.states[iDate] === "empty";
    },
  },
  watch: {
    currentDate: {
      handler(newValue) {
        if (newValue) {
          this.init(newValue);
        }
      },
      deep: true,
    },
  },
  methods: {
    upperFirst,
    async init(currentDate) {
      this.dates = [];
      this.dateStrs = [];
      for (let i = 0; i < this.nbDays; ++i) {
        const shift = Math.floor(i - this.nbDays / 2 + 1);
        const date = addDays(currentDate, shift);
        this.dates.push(date);
        this.dateStrs.push(date.toDateString());
      }
      this.dateStates = await API.userDays.daysStates(this.userId, { dates: this.dateStrs });
    },
    isCurrentDate(date) {
      return areSameDate(this.currentDate, date);
    },
    gotoYesterday() {
      this.changeDate(addDays(this.currentDate, -1));
    },
    gotoTomorrow() {
      this.changeDate(addDays(this.currentDate, +1));
    },
    changeDate(date) {
      if (this.isCurrentDate(date)) {
        return;
      }
      let baseUrl = this.baseUrl;
      if (isToday(date) && this.baseUrlToday) {
        baseUrl = this.baseUrlToday;
      } else if (isPast(date) && this.baseUrlPast) {
        baseUrl = this.baseUrlPast;
      } else if (isFuture(date) && this.baseUrlFuture) {
        baseUrl = this.baseUrlFuture;
      }
      this.$router.push({ name: baseUrl, params: { day: date.toDateString() } });
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
.op-day-selector {
  .day-cell {
    width: 150px;
  }

  .icon-cell {
    width: 60px;
  }
  .icon-cell.to_be_created {
    padding: 10px;
  }

  .to_be_created {
    color: $op-color-red;
  }
}
</style>
