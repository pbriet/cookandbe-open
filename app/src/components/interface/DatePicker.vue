<template>
  <div>
    <div class="op-date-picker">
      <select
        class="form-control form-select day-picker"
        name="day"
        v-model="dayValue"
        :class="{ 'op-invalid-input': showInvalidFields && !dayValue }"
        :required="required"
      >
        <option v-for="day in days" :value="day" :key="day">{{ day }}</option>
      </select>
      <select
        class="form-control form-select month-picker"
        name="month"
        v-model="monthValue"
        :class="{ 'op-invalid-input': showInvalidFields && !monthValue }"
        :required="required"
      >
        <option v-for="month in months" :value="month.id" :key="month.id">{{ month.caption }}</option>
      </select>
      <select
        class="form-control form-select year-picker"
        name="year"
        v-model="yearValue"
        :class="{ 'op-invalid-input': showInvalidFields && !yearValue }"
        :required="required"
      >
        <option v-for="year in years" :value="year" :key="year">{{ year }}</option>
      </select>
    </div>
    <div class="op-date-picker" v-if="withTime" style="margin-top: 15px">
      <label>Heure :</label>
      <select
        class="form-control form-select hour-picker"
        name="hour"
        v-model="hourValue"
        :class="{ 'op-invalid-input': showInvalidFields && !hourValue }"
        :required="required"
      >
        <option v-for="hour in hours" :value="hour" :key="hour">{{ hour }}</option>
      </select>
      <label id="minute-label">Minute :</label>
      <select
        class="form-control form-select minute-picker"
        name="minute"
        v-model="minuteValue"
        :class="{ 'op-invalid-input': showInvalidFields && !minuteValue }"
        :required="required"
      >
        <option v-for="minute in minutes" :value="minute" :key="minute">{{ minute }}</option>
      </select>
    </div>
  </div>
</template>

<script>
import { MONTH_CAPTIONS_IDS } from "@/common/static.js";

/*
 * This component adds a date-picker based with a bootstrap layout
 */
export default {
  name: "DatePicker",
  props: ["modelValue", "withTime", "required", "showInvalidFields"],
  data: () => {
    const days = [];
    for (let i = 1; i <= 31; i++) {
      days.push(i);
    }

    const currentYear = new Date().getFullYear();
    const years = [];
    for (let i = currentYear; i >= currentYear - 120; i--) {
      years.push(i);
    }

    const hours = [];
    for (let i = 0; i < 24; i++) {
      hours.push(i);
    }

    const minutes = [];
    for (let i = 0; i < 60; i++) {
      minutes.push(i);
    }

    return {
      minutes,
      hours,
      days,
      months: MONTH_CAPTIONS_IDS,
      years,
      minuteValue: null,
      hourValue: null,
      dayValue: null,
      monthValue: null,
      yearValue: null,
    };
  },
  mounted() {
    this.grabDetailsFromDate();
  },
  computed: {},
  watch: {
    modelValue() {
      this.grabDetailsFromDate();
    },
    yearValue() {
      this.onChangeFormValues();
    },
    monthValue() {
      this.onChangeFormValues();
    },
    dayValue() {
      this.onChangeFormValues();
    },
  },
  methods: {
    resetDate() {
      this.yearValue = null;
      this.monthValue = null;
      this.dayValue = null;
    },
    grabDetailsFromDate() {
      if (!this.modelValue) {
        this.resetDate();
        return;
      }

      const date = new Date(this.modelValue);
      this.yearValue = date.getFullYear();
      this.monthValue = date.getMonth() + 1;
      this.dayValue = date.getDate();
      this.hourValue = date.getHours();
      this.minuteValue = date.getMinutes();
    },
    onChangeFormValues() {
      // Explicit non zero origin based index
      const JANUARY = 1;

      if (
        this.withTime &&
        this.hourValue !== null &&
        this.minuteValue !== null &&
        this.yearValue !== null &&
        this.monthValue !== null &&
        this.dayValue !== null
      ) {
        this.$emit(
          "update:modelValue",
          new Date(
            this.yearValue,
            this.monthValue - JANUARY,
            this.dayValue,
            this.hourValue,
            this.minuteValue
          ).toISOString()
        );
      } else if (!this.withTime && this.yearValue !== null && this.monthValue !== null && this.dayValue !== null) {
        this.$emit(
          "update:modelValue",
          new Date(this.yearValue, this.monthValue - JANUARY, this.dayValue).toISOString()
        );
      }
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
.op-date-picker {
  $day-min-width: 45px;
  $month-min-width: 100px;
  $year-min-width: 65px;
  $hour-width: 90px;
  $minute-width: 90px;
  $layout-width: 10px; // borders, radius, ...
  $radius-width: $op-radius-md;
  $total-min-width: ($day-min-width + $month-min-width + $year-min-width + $layout-width);

  min-width: $total-min-width;
  max-width: ($total-min-width * 1.5);
  display: table;
  width: 100%;

  @media (min-width: $total-min-width) {
    select {
      padding: 0px;
      border-radius: 0px;
      display: table-cell;
      border-right: 0px;
    }

    select:first-child {
      border-top-left-radius: $radius-width;
      border-bottom-left-radius: $radius-width;
    }

    select:last-child {
      border-top-right-radius: $radius-width;
      border-bottom-right-radius: $radius-width;
      border-right: 1px solid $op-color-border;
    }

    .day-picker {
      min-width: $day-min-width;
      width: 22%;
    }

    .month-picker {
      min-width: $month-min-width;
      width: 47%;
    }

    .year-picker {
      min-width: $year-min-width;
      width: 31%;
    }
    .hour-picker {
      width: $hour-width;
    }
    .minute-picker {
      width: $minute-width;
    }
    #minute-label {
      margin-left: 20px;
    }
    label {
      margin-right: 5px;
    }
  }

  @media (max-width: $total-min-width) {
    select {
      width: 100%;
      border-radius: $radius-width;
    }
  }
}
</style>
