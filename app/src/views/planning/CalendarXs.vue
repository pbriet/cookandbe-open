<template>
  <div class="op-table">
    <div
      class="op-row"
      v-for="day in planningDays"
      :key="day.date"
      @click="clickDay(day)"
      @mouseenter="$emit('update:selection', { activeDay: day.date })"
      @mouseleave="$emit('update:selection', { activeDay: null })"
      :class="{
        'empty-column': !day.filled,
        selected_meal_slot: selection.activeDay == day.date,
        clickable_meal_slot: day.clickable,
        past_day: day.isPast,
        present_day: day.isToday,
        future_day: day.isFuture,
      }"
    >
      <div class="op-cell" style="width: 150px">
        <RecipeImg :recipe="day.focusedRecipe" />
      </div>
      <div class="op-cell">
        <h4 class="col-12" v-if="!day.isToday">
          {{ upperFirst(DateTime.fromJSDate(day.date).setLocale("fr").toFormat(dateFormat)) }}
        </h4>
        <h4 class="col-12" v-if="day.isToday">Aujourd'hui</h4>
        <span class="col-12" v-if="day.filled">
          <FontAwesomeIcon :icon="['fas', 'check']" /> Vous avez {{ nbPlannedMeals(day) }} repas planifiés
        </span>
        <span class="col-12 mt-2" v-if="day.skipped">
          <FontAwesomeIcon :icon="['fas', 'ban']" /> Vous ne souhaitez pas de suggestions
        </span>
        <span class="col-12 mt-2" v-if="!day.filled && !day.skipped && day.isFutureOrToday">
          <FontAwesomeIcon :icon="['fas', 'plus']" /> Cliquez pour planifier !
        </span>
        <span class="col-12 mt-2" v-if="!day.filled && !day.skipped && !day.isFutureOrToday">
          <FontAwesomeIcon :icon="['fas', 'times']" /> Non renseigné
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { sortBy, upperFirst } from "lodash";
import RecipeImg from "@/components/recipe/RecipeImg.vue";
import { DateTime } from "luxon";

export default {
  name: "CalendarXs",
  props: ["planning", "dateFormat", "clickDay", "selection"],
  data: () => ({ DateTime }),
  computed: {
    planningDays() {
      return sortBy(this.planning.days, (day) => day.date);
    },
  },
  methods: {
    upperFirst,
    nbPlannedMeals(day) {
      return Object.keys(day.mealSlots).length;
    },
  },
  components: { RecipeImg },
};
</script>

<style scoped lang="scss"></style>
