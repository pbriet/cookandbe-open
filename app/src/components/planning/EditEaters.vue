<template>
  <div class="edit-eaters">
    <div class="dialog-title" v-show="withTitle">Modifier les présences</div>
    <div class="dialog-body">
      <ul class="eater-list">
        <li v-for="eater in eaters" :key="eater.id">
          <CheckBox
            :modelValue="eater.selected"
            :caption="eater.profile.nickname"
            :onChange="() => toggleEater(eater)"
            :disabled="eater.profile.isMainProfile"
          />
        </li>
      </ul>

      <button class="btn btn-secondary" id="validate-eaters" @click="validate" :disabled="validating">
        Valider les modifications
      </button>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { includes } from "lodash";
import CheckBox from "@/components/interface/CheckBox.vue";
import API from "@/api.js";

/*
 * This component displays a multiple choice of eaters
 */
export default {
  name: "EditEaters",
  props: ["mealslotId", "mealslotEaterIds", "onValidated", "withTitle"],
  data: () => ({
    eaters: [],
    validating: false,
  }),
  mounted() {
    this.reset(this.mealslotId);
  },
  computed: {
    ...mapGetters({
      userId: "user/id",
    }),
  },
  watch: {
    mealslotId: {
      handler(newValue) {
        // When mealslot is initialized, or changes, update the data
        if (newValue) {
          this.reset(newValue);
        }
      },
      deep: true,
    },
  },
  methods: {
    async reset() {
      this.validating = null;
      if (this.eaters.length == 0) {
        // First call : load the eaters
        this.eaters = (await API.eaters(this.userId)).map((eater) => ({ ...eater, selected: false }));
      }
      this.detectEaterSelection();
    },
    validate() {
      this.validating = true;
      // Using a timeout applies the modifications right now, disabling the "validate" button.
      setTimeout(() => {
        this.onValidated();
        this.validating = null;
      }, 10);
    },
    /*
     * Store a "selected" attribute within the mealslot eaters
     */
    detectEaterSelection() {
      for (const eater of this.eaters) {
        // We detect if the eater is included in the current selected mealslot
        eater.selected = includes(this.mealslotEaterIds, eater.id);
      }
    },
    toggleEater(eater) {
      if (eater.profile.isMainProfile) {
        return;
      }
      eater.selected = !eater.selected;
      let apiFcn;
      if (eater.selected) {
        apiFcn = API.mealSlot.addEater;
      } else {
        apiFcn = API.mealSlot.removeEater;
      }
      apiFcn(this.mealslotId, { eaterId: eater.id });
    },
  },
  components: { CheckBox },
};
</script>

<style scoped lang="scss">
.edit-eaters {
  color: $op-color-text-main;

  .eater-list {
    margin-top: 10px;
    list-style-type: none;
  }
  ul {
    padding-left: 10px;
  }
  #validate-eaters {
    margin-top: 5px;
    margin-left: 10px;
  }
}
</style>
