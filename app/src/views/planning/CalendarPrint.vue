<template>
  <h2 class="op-vs-5">Votre planning de la semaine</h2>

  <table class="calendar" ref="calendar">
    <tr>
      <th
        class="calendar-day-title"
        v-for="day in planning.days"
        :key="day.date"
        :class="{ clickable_meal_slot: day.clickable }"
      >
        <h4>
          {{ upperFirst(DateTime.fromJSDate(day.date).setLocale("fr").toFormat(dateFormat)) }}
        </h4>
      </th>
    </tr>
    <tr v-for="(mealType, index) in planning.mealTypes" :key="mealType.id">
      <td
        class="meal_slot"
        :rowspan="day.filled ? 1 : planning.mealTypes.length"
        v-for="day in planningDays"
        :key="day.date"
        v-show="day.filled || index == 0"
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
import { DateTime } from "luxon";

export default {
  name: "CalendarPrint",
  props: ["planning", "dateFormat"],
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
  components: {},
};
</script>

<style scoped lang="scss"></style>
