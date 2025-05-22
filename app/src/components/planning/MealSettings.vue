<template>
  <div class="meal-settings">
    <div class="meal-setting op-clickable-link" v-if="speedElt.speed">
      <span class="op-icon-md me-1">
        <FontAwesomeIcon :icon="['far', 'clock']" />
      </span>
      <span class="speed_value">
        <select :value="speedElt.speed" v-show="editing.speed" @change="changeSpeed">
          <option v-for="speedOption in HABITS_SPEED_OPTIONS" :value="speedOption.id" :key="speedOption.id">
            {{ speedOption.shortLabel }}
          </option>
        </select>
        <span class="speed_display" v-show="!editing.speed" @click="editing.speed = true">
          {{ getSpeedLabel(speedElt.speed) }}
        </span>
      </span>
    </div>

    <div class="meal-setting op-clickable-link" v-if="eaters && eatenAtHome" @click="onEditEaters">
      <span class="op-icon-md me-1">
        <FontAwesomeIcon :icon="['fas', 'user']" />
      </span>
      <span class="nb_eaters">
        {{ eaters.length }}
      </span>
    </div>

    <!-- <div class="meal-setting op-clickable-link" @click="onAddDish" v-if="allowMealEdit">
		 <FontAwesomeIcon :icon="['fas', 'plus']" />
		 <span>Ajouter un plat</span>
		 </div> -->
  </div>
</template>

<script>
import { HABITS_SPEED_OPTIONS } from "@/common/static.js";
import { find } from "lodash";
/*
 * Edition of speed and eaters for a meal
 */
export default {
  name: "MealSettings",
  props: [
    "speedElt", // Element containing a "speed" attribute
    "eaters",
    "allowMealEdit",
    "eatenAtHome",
    "onChangeSpeed",
    "onAddDish",
    "onEditEaters",
  ],
  data: () => ({
    HABITS_SPEED_OPTIONS,
    editing: {},
  }),
  computed: {},
  methods: {
    getSpeedLabel(val) {
      return find(HABITS_SPEED_OPTIONS, ["id", val]).shortLabel;
    },
    changeSpeed(event) {
      this.editing.speed = null;
      this.onChangeSpeed(parseInt(event.target.value, 10));
    },
  },
  components: {},
};
</script>

<style scoped lang="scss">
.meal-settings {
  display: inline-block;
  font-size: $op-font-md;

  .meal-setting {
    margin-right: 14px;
    display: inline-flex;

    select {
      color: $op-color-text-main;
      background-color: white;
    }
  }
}
</style>
