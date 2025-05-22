<template>
  <div class="day-meal-place-editor">
    <h3 class="dialog-title">Structure de la journée</h3>

    <div class="dialog-body">
      <div
        v-for="(row, index) in structure?.structure || []"
        :key="row.mealType.id"
        class="row"
        :class="{ odd_item: index % 2 == 1, even_item: index % 2 == 0, first_item: index == 0 }"
      >
        <div class="col-12 col-md-3 d-flex align-items-center">
          <h5 class="m-0">{{ row.mealType.name }}</h5>
        </div>
        <div class="col-12 col-md-5 d-flex align-items-center">
          <Select
            :options="options"
            :modelValue="row.mealPlace.key"
            @update:modelValue="changeMealPlace(row, $event)"
            selectClasses="selectpicker w-100"
            buttonClasses="btn-secondary w-100"
          >
            <template v-slot:option="{ option }">
              <img class="op-icon-lg" :src="option.img" /> {{ option.label }}
            </template>
          </Select>
        </div>
        <div class="col-12 col-md-4" v-if="row.suggest">
          <MealSettings
            :speedElt="row"
            :eaters="row.eaterIds"
            :allowMealEdit="false"
            :eatenAtHome="row.mealPlace.key === 'home'"
            :onChangeSpeed="(speed) => onChangeSpeed(row, speed)"
            :onEditEaters="() => onEditEaters(row)"
          />
        </div>
        <transition name="eaters">
          <div class="col-12 edit-eaters-section" v-show="row.editEaters">
            <EditEaters
              :mealslotId="row.mealSlotId"
              :mealslotEaterIds="row.eaterIds"
              :onValidated="() => onEditedMealslotEaters(row)"
            />
          </div>
        </transition>
      </div>
      <!-- row -->

      <button class="btn btn-success" @click="onValidate" id="validate-structure-btn">
        Appliquer les modifications
      </button>
    </div>
  </div>
</template>

<script>
import { PLACES } from "@/common/static.js";
import { mapGetters } from "vuex";
import { each } from "lodash";
import API from "@/api.js";
import Select from "@/components/interface/Select.vue";
import MealSettings from "@/components/planning/MealSettings.vue";
import EditEaters from "@/components/planning/EditEaters.vue";

export default {
  name: "DayMealPlaceEditor",
  props: [
    "date",
    "onValidate",
    // Contains:
    // recalc: Boolean that is set to true if some modifications requires a recalculation
    // reload: Boolean that is set to true if some modifications requires to reload the day content
    "mealPlaceEdition",
  ],
  data: () => ({
    structure: null,
  }),
  mounted() {
    this.reloadStructure();
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
    }),
    options() {
      return Object.values(PLACES).map((place) => ({
        value: place.key,
        label: place.shortLabel,
        img: require(`@/assets/img/${place.img}`),
      }));
    },
  },
  methods: {
    async reloadStructure(onlyRow) {
      const values = await API.userDay.structure(this.userId, this.date.toDateString());
      if (!onlyRow) {
        this.structure = values;
        return;
      }
      var i;
      // Updating only a specific row
      for (i = 0; i < values.structure.length; i++) {
        if (values.structure[i].mealType.id == onlyRow.mealType.id) {
          break;
        }
      }
      this.updateRow(i, values.structure[i]);
    },
    /*
     * Update a row, except mealPlace - so that select picker still works
     */
    updateRow(i, data) {
      // Quite ugly : iterating on previous keys and new keys of object to update
      const keys = Object.keys(data).concat(Object.keys(this.structure.structure[i]));
      each(keys, (key) => {
        this.structure.structure[i][key] = data[key];
      });
    },
    /*
     * Changing the mealPlace of a meal
     */
    async changeMealPlace(row, value) {
      row.mealPlace.key = value;
      row.editEaters = false;
      const data = await API.userDay.setMealPlace(this.userId, this.date.toDateString(), {
        mealTypeId: row.mealType.id,
        mealPlaceKey: row.mealPlace.key,
      });
      if (data.status === "error") {
        console.log("Error while changing meal place - closing popup");
        this.onValidate();
        return;
      }
      this.$emit("update:mealPlaceEdition", {
        reload: true,
        recalc: true,
      });
      this.reloadStructure(row);
    },
    /*
     * Changing the speed of a meal
     */
    async onChangeSpeed(row, speed) {
      row.speed = speed;
      this.$emit("update:mealPlaceEdition", {
        ...this.mealPlaceEdition,
        reload: true,
      });
      const data = await API.mealSlot.setSpeed(row.mealSlotId, { speed });
      if (data.previousValue > speed) {
        // User has less time than expected : a recalculation is required
        this.$emit("update:mealPlaceEdition", {
          ...this.mealPlaceEdition,
          recalc: true,
        });
      }
    },
    /*
     * Clicking on the eaters (open the panel)
     */
    onEditEaters(row) {
      if (!row.editEaters) {
        row.editEaters = true;
      } else {
        this.onEditedMealslotEaters(row);
      }
    },
    /*
     * Changing the eaters
     */
    onEditedMealslotEaters(row) {
      row.editEaters = null; // Closing panel
      this.reloadStructure(row);
      // No need to recalculate
      this.$emit("update:mealPlaceEdition", {
        ...this.mealPlaceEdition,
        reload: true,
      });
    },
  },
  components: { EditEaters, Select, MealSettings },
};
</script>

<style lang="scss">
.day-meal-place-editor {
  .meal-setting {
    width: 90px;
    display: flex !important;
  }
  .row {
    padding-top: 5px;
    padding-bottom: 5px;
    border-bottom: 1px solid $op-color-border;
  }
  .first_item {
    border-top: 1px solid $op-color-border;
  }
  .odd_item {
    background-color: $op-color-table-row-odd;
  }
  .even_item {
    background-color: $op-color-table-row-even;
  }
  h5 {
    font-weight: bold;
  }
  #validate-structure-btn {
    float: right;
    margin-top: 15px;
  }
  .eaters-enter-active,
  .eaters-leave-active {
    transition: 0.2s ease-in-out all;
    overflow: hidden;
  }

  .eaters-enter-from,
  .eaters-leave-to {
    opacity: 0;
    max-height: 0;
  }
  .eaters-leave-from,
  .eaters-enter-to {
    opacity: 1;
    max-height: 200px;
  }
}
</style>
