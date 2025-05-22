<template>
  <table class="calendar" ref="calendar">
    <tr>
      <th
        class="calendar-day-title"
        v-for="day in planning.days"
        :key="day.date"
        @mouseenter="$emit('update:selection', { activeDay: day.date })"
        @mouseleave="$emit('update:selection', { activeDay: null })"
        :class="{ clickable_meal_slot: day.clickable }"
        @click="clickDay(day)"
      >
        <RecipeImg :recipe="day.focusedRecipe" :withBorder="true">
          <div class="overlay-row-void"></div>
          <div class="overlay-row">
            <div
              class="overlay-cell"
              :class="{
                selected_meal_slot: selection.activeDay == day.date,
                clickable_meal_slot: day.clickable,
                present_day: day.isToday,
              }"
            >
              {{ upperFirst(DateTime.fromJSDate(day.date).setLocale("fr").toFormat(dateFormat)) }}
            </div>
          </div>
        </RecipeImg>
      </th>
    </tr>
    <tr v-for="(mealType, index) in planning.mealTypes" :key="mealType.id">
      <td
        class="meal_slot"
        :rowspan="day.filled ? 1 : planning.mealTypes.length"
        v-for="day in planningDays"
        :key="day.date"
        @click="clickDay(day)"
        v-show="day.filled || index == 0"
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
        <!-- Plan a new day -->
        <div v-if="!day.filled && day.isFutureOrToday && !day.shoppingListId">
          <span class="op-icon-xxl" v-if="!day.skipped">
            <FontAwesomeIcon :icon="['fas', 'plus']" />
          </span>
          <span v-if="day.skipped">
            <span class="op-icon-xxxl"> <FontAwesomeIcon :icon="['fas', 'ban']" /> </span><br />
            <span class="op-font-xs">Vous ne souhaitez pas de suggestions</span>
          </span>
        </div>

        <!-- Dishes -->
        <template v-if="!day.mealSlots[mealType.id].place">
          <div class="dish" v-for="dish in dishes(day.mealSlots[mealType.id])" :key="dish.order">
            <!-- Display of recipes -->
            <div v-if="day.filled">
              <p class="dish_recipe" v-for="recipe in dish.recipes" :key="recipe.id">
                {{ recipe.name }}
              </p>
            </div>
          </div>
        </template>

        <!-- Place -->
        <div style="text-align: center" v-if="day.mealSlots[mealType.id].place">
          <img class="op-icon-dxl" :src="placeImg(day.mealSlots[mealType.id].place.img)" />
        </div>
      </td>
    </tr>
  </table>
</template>

<script>
import { sortBy, upperFirst } from "lodash";
import RecipeImg from "@/components/recipe/RecipeImg.vue";
import { DateTime } from "luxon";

export default {
  name: "CalendarLg",
  props: ["planning", "dateFormat", "clickDay", "selection"],
  data: () => ({ DateTime }),
  computed: {
    planningDays() {
      return sortBy(this.planning.days, (day) => day.date);
    },
  },
  methods: {
    upperFirst,
    dishes(mealSlot) {
      return sortBy(mealSlot.dishes, (dish) => dish.order);
    },
    placeImg(place) {
      return require(`@/assets/img/${place}`);
    },
  },
  components: { RecipeImg },
};
</script>

<style scoped lang="scss"></style>
