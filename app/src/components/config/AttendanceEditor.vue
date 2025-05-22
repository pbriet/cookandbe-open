<template>
  <h3 class="dialog-title">{{ selectedMeal.name }} - {{ selectedColumn.name }}</h3>
  <div class="dialog-body">
    <div class="attendance-editor-infos">Indiquez la façon dont vous prenez ce repas.</div>
    <div v-for="place in allowedPlaces" :key="place.label">
      <button class="btn btn-secondary attendance-editor-button" @click="onChangeAttendance(place)">
        <img class="attendance-editor-icon" :src="placeImg(place.img)" />
        <span class="attendance-editor-place">{{ place.label }}</span>
      </button>
    </div>
    <div style="clear: both" />
  </div>
</template>

<script>
import { PLACES } from "@/common/static.js";
import { pickBy } from "lodash";

/*
 * This component adds a panel to edit a meal slot on the planning
 */
export default {
  name: "AttendanceEditor",
  props: ["selectedMeal", "selectedColumn", "allowDoNotEat", "changeAttendanceFcn"],
  data: () => ({
    places: PLACES,
  }),
  computed: {
    allowedPlaces() {
      return pickBy(this.places, this.allowPlace);
    },
  },
  methods: {
    // Can this place be selected ?
    allowPlace(place) {
      if (this.allowDoNotEat) {
        return true;
      }
      return place.key != "donoteat";
    },
    onChangeAttendance(place) {
      this.changeAttendanceFcn(this.selectedMeal, this.selectedColumn, place);
    },
    placeImg(place) {
      return require(`@/assets/img/${place}`);
    },
  },
  components: {},
};
</script>

<style scoped lang="scss"></style>
